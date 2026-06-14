"""Payment endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.subscription import Payment
from app.services.pawapay_service import PawaPayService, get_correspondent_code
from app.services.subscription_service import SubscriptionService
from app.services.pricing_service import PricingService
from app.services.trial_service import TrialService
from app.services.crypto_payment_service import crypto_payment_service
from app.services.email_service import EmailService
from app.core.config import settings
from pydantic import BaseModel
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

router = APIRouter()


class InitiatePaymentRequest(BaseModel):
    plan_name: str
    phone_number: str
    country: str
    operator: str


class PaymentResponse(BaseModel):
    payment_id: str
    status: str
    message: str


class CryptoPaymentRequest(BaseModel):
    plan_name: str  # 'personal' or 'professional'
    token_symbol: str  # 'USDT' or 'USDC'


class CryptoPaymentVerifyRequest(BaseModel):
    payment_id: str
    transaction_hash: str


@router.post("/initiate", response_model=PaymentResponse)
async def initiate_payment(
    request: InitiatePaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Initiate mobile money payment with local currency pricing."""

    # Validate plan name
    if request.plan_name not in ['personal', 'professional']:
        raise HTTPException(status_code=400, detail="Invalid plan. Choose 'personal' or 'professional'")

    # Get pricing for country with live exchange rates
    try:
        country_pricing = await PricingService.get_country_pricing(request.country)
        amount = country_pricing[request.plan_name]  # Get personal or professional price
        currency = country_pricing["currency"]
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=400, detail=f"Pricing not available for {request.country}")

    # Get PawaPay correspondent code
    operators = PricingService.get_operators(request.country)
    correspondent = operators.get(request.operator)
    if not correspondent:
        raise HTTPException(
            status_code=400,
            detail=f"Operator {request.operator} not supported in {request.country}"
        )

    # Create payment record
    payment = Payment(
        user_id=current_user.id,
        amount=amount,
        currency=currency,
        payment_method="mobile_money",
        provider=request.operator,
        phone_number=request.phone_number,
        country=request.country,
        status="pending"
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    # Initiate PawaPay deposit
    pawapay = PawaPayService(settings.PAWAPAY_API_TOKEN)

    result = pawapay.initiate_deposit(
        amount=amount,
        currency=currency,
        phone_number=request.phone_number,
        correspondent=correspondent,
        statement_description=f"ACTI {request.plan_name.title()} Plan"
    )
    
    payment.external_reference = result["deposit_id"]
    payment.transaction_id = str(payment.id)
    db.commit()
    
    if result["success"]:
        return PaymentResponse(
            payment_id=str(payment.id),
            status="pending",
            message="Payment initiated. Check your phone."
        )
    else:
        payment.status = "failed"
        db.commit()
        raise HTTPException(status_code=400, detail="Payment failed")


@router.get("/status/{payment_id}")
async def check_payment_status(
    payment_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check payment status."""
    payment = db.query(Payment).filter(
        Payment.id == uuid.UUID(payment_id),
        Payment.user_id == current_user.id
    ).first()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    if payment.external_reference and payment.status == "pending":
        pawapay = PawaPayService(settings.PAWAPAY_API_TOKEN)
        result = pawapay.check_deposit_status(payment.external_reference)

        if result["success"] and result["status"] == "COMPLETED":
            payment.status = "completed"
            payment.paid_at = datetime.utcnow()

            # Create/extend subscription (30 days)
            from app.models.subscription import Subscription as SubscriptionModel
            existing = db.query(SubscriptionModel).filter(
                SubscriptionModel.user_id == current_user.id,
                SubscriptionModel.status == "active"
            ).first()

            if existing:
                # Extend existing subscription by 30 days
                existing.expires_at = existing.expires_at + timedelta(days=30)
            else:
                # Create new subscription
                # Get plan name from current user's account type or fallback
                plan_name = current_user.account_type if current_user.account_type else 'personal'
                SubscriptionService.create_subscription(
                    db, current_user.id, plan_name, duration_days=30
                )

            # Convert trial status
            current_user.trial_status = 'converted'

            db.commit()

            # Send payment receipt email
            try:
                # Get the active subscription to get expiry date
                subscription = db.query(SubscriptionModel).filter(
                    SubscriptionModel.user_id == current_user.id,
                    SubscriptionModel.status == "active"
                ).first()

                plan_name = subscription.plan_name if subscription else (current_user.account_type or 'starter')
                subscription_expires = subscription.expires_at.strftime("%B %d, %Y") if subscription else "N/A"

                EmailService.send_payment_receipt(
                    to_email=current_user.email,
                    payment_id=str(payment.id),
                    plan_name=plan_name,
                    amount=str(int(payment.amount)),
                    currency=payment.currency,
                    payment_method=f"Mobile Money ({payment.provider})",
                    payment_date=payment.paid_at.strftime("%B %d, %Y at %I:%M %p"),
                    subscription_expires=subscription_expires
                )
                print(f"[PAYMENT] Receipt email sent to {current_user.email}")
            except Exception as email_error:
                print(f"[PAYMENT] Failed to send receipt email: {email_error}")
                # Don't fail the payment if email fails

    return {
        "payment_id": str(payment.id),
        "status": payment.status,
        "amount": float(payment.amount),
        "currency": payment.currency
    }


@router.get("/subscription")
async def get_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current subscription status."""
    subscription = SubscriptionService.get_active_subscription(db, current_user.id)

    # Check trial status
    trial_active = TrialService.check_trial_active(current_user, db)
    days_remaining = TrialService.days_remaining(current_user)

    if not subscription:
        return {
            "plan": current_user.account_type or "personal",
            "status": "trial" if trial_active else "inactive",
            "trial_active": trial_active,
            "days_remaining": days_remaining,
            "expires_at": current_user.trial_ends_at.isoformat() if current_user.trial_ends_at else None
        }

    return {
        "plan": subscription.plan_name,
        "status": subscription.status,
        "expires_at": subscription.expires_at.isoformat(),
        "trial_active": False,
        "days_remaining": 0
    }


@router.get("/pricing")
async def get_pricing():
    """Get pricing for all 20 countries with live exchange rates."""
    countries = await PricingService.list_all_pricing()
    return {
        "countries": countries
    }


@router.get("/pricing/{country_code}")
async def get_country_pricing(country_code: str):
    """Get pricing for specific country with live exchange rates."""
    try:
        pricing = await PricingService.get_country_pricing(country_code)
        return pricing
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/initiate-crypto")
async def initiate_crypto_payment(
    request: CryptoPaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Initiate crypto payment (USDT/USDC on Polygon).

    Returns payment details including wallet address and amount.
    User needs to send the payment from their wallet.
    """
    # Validate inputs
    if request.plan_name not in ['personal', 'professional']:
        raise HTTPException(status_code=400, detail="Invalid plan. Choose 'personal' or 'professional'")

    if request.token_symbol not in ['USDT', 'USDC']:
        raise HTTPException(status_code=400, detail="Invalid token. Choose 'USDT' or 'USDC'")

    # Get USD price for plan
    plan_prices = {
        'personal': Decimal('5.00'),
        'professional': Decimal('49.00')
    }

    amount_usd = plan_prices[request.plan_name]

    # Create payment request
    payment_details = crypto_payment_service.create_payment_request(
        amount_usd=amount_usd,
        token_symbol=request.token_symbol,
        user_id=str(current_user.id),
        plan_name=request.plan_name
    )

    # Create payment record in database
    payment = Payment(
        user_id=current_user.id,
        amount=amount_usd,
        currency="USD",
        payment_method="crypto",
        provider=f"Polygon_{request.token_symbol}",
        country="CRYPTO",
        status="pending"
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return {
        "payment_id": str(payment.id),
        "status": "pending",
        "payment_details": payment_details
    }


@router.post("/verify-crypto")
async def verify_crypto_payment(
    request: CryptoPaymentVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verify crypto payment transaction.

    User submits their transaction hash after sending payment.
    We verify the transaction on-chain and activate subscription if valid.
    """
    # Get payment record
    payment = db.query(Payment).filter(
        Payment.id == uuid.UUID(request.payment_id),
        Payment.user_id == current_user.id
    ).first()

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if payment.status == "completed":
        return {
            "verified": True,
            "message": "Payment already verified and processed"
        }

    # Extract token symbol from provider field
    token_symbol = payment.provider.split('_')[1] if '_' in payment.provider else 'USDT'

    # Verify the transaction on-chain
    verification = await crypto_payment_service.verify_payment(
        transaction_hash=request.transaction_hash,
        expected_amount=Decimal(str(payment.amount)),
        token_symbol=token_symbol
    )

    if not verification['verified']:
        return {
            "verified": False,
            "error": verification.get('error', 'Payment verification failed')
        }

    # Payment verified - update payment record
    payment.status = "completed"
    payment.paid_at = datetime.utcnow()
    payment.external_reference = request.transaction_hash
    payment.transaction_id = str(payment.id)

    # Determine plan name from payment amount
    plan_name = 'personal' if payment.amount <= 10 else 'professional'

    # Create or extend subscription (30 days)
    from app.models.subscription import Subscription as SubscriptionModel
    existing = db.query(SubscriptionModel).filter(
        SubscriptionModel.user_id == current_user.id,
        SubscriptionModel.status == "active"
    ).first()

    if existing:
        # Extend existing subscription by 30 days
        existing.expires_at = existing.expires_at + timedelta(days=30)
    else:
        # Create new subscription
        SubscriptionService.create_subscription(
            db, current_user.id, plan_name, duration_days=30
        )

    # Convert trial status
    current_user.trial_status = 'converted'

    db.commit()

    # Send payment receipt email
    try:
        # Get the active subscription to get expiry date
        subscription = db.query(SubscriptionModel).filter(
            SubscriptionModel.user_id == current_user.id,
            SubscriptionModel.status == "active"
        ).first()

        subscription_expires = subscription.expires_at.strftime("%B %d, %Y") if subscription else "N/A"

        EmailService.send_payment_receipt(
            to_email=current_user.email,
            payment_id=str(payment.id),
            plan_name=plan_name,
            amount=str(int(payment.amount)),
            currency=payment.currency,
            payment_method=f"Crypto ({token_symbol})",
            payment_date=payment.paid_at.strftime("%B %d, %Y at %I:%M %p"),
            subscription_expires=subscription_expires
        )
        print(f"[PAYMENT] Receipt email sent to {current_user.email}")
    except Exception as email_error:
        print(f"[PAYMENT] Failed to send receipt email: {email_error}")
        # Don't fail the payment if email fails

    return {
        "verified": True,
        "message": "Payment verified successfully! Your subscription is now active.",
        "transaction_hash": request.transaction_hash,
        "plan": plan_name,
        "duration_days": 30
    }


@router.get("/crypto-status/{payment_id}")
async def check_crypto_payment_status(
    payment_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check status of crypto payment."""
    payment = db.query(Payment).filter(
        Payment.id == uuid.UUID(payment_id),
        Payment.user_id == current_user.id
    ).first()

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    result = {
        "payment_id": str(payment.id),
        "status": payment.status,
        "amount": float(payment.amount),
        "currency": payment.currency,
        "provider": payment.provider
    }

    # If payment has transaction hash, get on-chain status
    if payment.external_reference:
        chain_status = await crypto_payment_service.get_payment_status(
            payment.external_reference
        )
        result["chain_status"] = chain_status

    return result
