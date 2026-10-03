# 🔀 PawaPay Webhook Router - Visual Flow

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         PAWAPAY                                 │
│                    (Payment Gateway)                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Single Webhook URL
                             │ POST /api/payments/webhooks/pawapay
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              AFRICA CYBER TRUST BACKEND                         │
│         https://africa-cyber-trust.onrender.com                 │
│                                                                 │
│  🔀 WEBHOOK ROUTER (payments.py)                                │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  Step 1: Check local database                                  │
│  ┌──────────────────────────────┐                              │
│  │ Query: depositId in DB?      │                              │
│  └──────────┬───────────────────┘                              │
│             │                                                   │
│         ✅ FOUND                                                │
│             │                                                   │
│             ▼                                                   │
│  ┌──────────────────────────────┐                              │
│  │ Process ACT Payment:         │                              │
│  │ • Update payment status      │                              │
│  │ • Activate subscription      │                              │
│  │ • Send receipt email         │                              │
│  │ • Process agent commissions  │                              │
│  └──────────────────────────────┘                              │
│             │                                                   │
│             └──► RETURN SUCCESS ✅                              │
│                                                                 │
│         ❌ NOT FOUND                                            │
│             │                                                   │
│             ▼                                                   │
│  Step 2: Forward to Haraka                                     │
│  ┌──────────────────────────────┐                              │
│  │ POST to Haraka backend       │──────────────┐               │
│  └──────────────────────────────┘              │               │
└─────────────────────────────────────────────────┼───────────────┘
                                                  │
                                                  ▼
                              ┌───────────────────────────────────┐
                              │     HARAKA BACKEND                │
                              │ harakabackend.onrender.com        │
                              │                                   │
                              │ POST /api/v1/payments/webhooks/   │
                              │      pawapay                      │
                              │                                   │
                              │ • Find order by depositId         │
                              │ • Update order status             │
                              │ • Confirm payment                 │
                              │ • Notify customer                 │
                              │ • Notify courier/restaurant       │
                              └─────────────┬─────────────────────┘
                                            │
                              ✅ Returns 200 │
                                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              AFRICA CYBER TRUST BACKEND                         │
│                                                                 │
│  ┌──────────────────────────────┐                              │
│  │ Haraka handled payment ✅     │                              │
│  └──────────────────────────────┘                              │
│             │                                                   │
│             └──► RETURN Haraka's response                       │
│                                                                 │
│         ❌ Haraka returns error or timeout                      │
│             │                                                   │
│             ▼                                                   │
│  Step 3: Forward to EscoPay/DDA                                │
│  ┌──────────────────────────────┐                              │
│  │ Try 3 callbacks in parallel: │──────────────┐               │
│  │ 1. Cloud Run (Deposit)       │              │               │
│  │ 2. Cloud Function (Payout)   │              │               │
│  │ 3. Cloud Function (Refund)   │              │               │
│  └──────────────────────────────┘              │               │
└─────────────────────────────────────────────────┼───────────────┘
                                                  │
                    ┌─────────────────────────────┴────────────┐
                    │                                          │
                    ▼                                          ▼
    ┌───────────────────────────┐          ┌──────────────────────────┐
    │   ESCOPAY/DDA BACKENDS    │          │   ESCOPAY CLOUD          │
    │   (Cloud Run)             │          │   FUNCTIONS              │
    │                           │          │                          │
    │ pawapaydepositcallback-   │          │ pawapayPayoutCallback    │
    │ rwjfghh2ka-uc.a.run.app   │          │ pawapayRefundCallback    │
    │                           │          │                          │
    │ • Deposit handling        │          │ • Payout handling        │
    │ • Shared by EscoPay & DDA │          │ • Refund handling        │
    │ • Distinguishes by app    │          │                          │
    └─────────────┬─────────────┘          └──────────┬───────────────┘
                  │                                   │
    ✅ Returns 200 │                     ✅ Returns 200 │
                  └────────────┬──────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│              AFRICA CYBER TRUST BACKEND                         │
│                                                                 │
│  ┌──────────────────────────────┐                              │
│  │ EscoPay/DDA handled ✅        │                              │
│  └──────────────────────────────┘                              │
│             │                                                   │
│             └──► RETURN their response                          │
│                                                                 │
│         ❌ Not found in any app                                 │
│             │                                                   │
│             ▼                                                   │
│  ┌──────────────────────────────┐                              │
│  │ RETURN ERROR:                │                              │
│  │ "Payment not found in:       │                              │
│  │  - Africa Cyber Trust        │                              │
│  │  - Haraka                    │                              │
│  │  - EscoPay                   │                              │
│  │  - DDA"                      │                              │
│  └──────────────────────────────┘                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Routing Decision Tree

```
PawaPay Webhook Received
         │
         ▼
┌────────────────────┐
│ Check ACT database │
└────────┬───────────┘
         │
    ┌────┴────┐
    │         │
 Found    Not Found
    │         │
    ▼         ▼
 Process   Forward to Haraka
  ACT          │
Payment    ┌───┴────┐
    │      │        │
    ▼   Success  Failed
 Return     │        │
 200 ✅     ▼        ▼
       Return   Forward to
       200 ✅   EscoPay/DDA
                    │
               ┌────┴────┐
               │         │
            Success   Failed
               │         │
               ▼         ▼
            Return    Return
            200 ✅    404 ❌
```

---

## Example: Haraka Payment Flow

### Timeline:

```
T+0s   Customer places order in Haraka app
       Amount: 5,000 RWF
       Payment method: MTN Mobile Money

T+1s   Haraka backend initiates PawaPay deposit
       depositId: "550e8400-e29b-41d4-a716-446655440001"
       Status: PENDING

T+2s   Customer receives prompt on phone
       "Confirm payment of 5,000 RWF to Haraka?"

T+5s   Customer enters PIN and confirms
       MTN processes payment

T+7s   PawaPay receives confirmation from MTN
       Status: COMPLETED
       
T+8s   PawaPay sends webhook to:
       https://africa-cyber-trust.onrender.com/api/payments/webhooks/pawapay
       
       Payload:
       {
         "depositId": "550e8400-e29b-41d4-a716-446655440001",
         "status": "COMPLETED",
         "amount": "5000.00",
         "currency": "RWF",
         "correspondent": "MTN_MOMO_RWA"
       }

T+9s   Africa Cyber Trust Webhook Router:
       [WEBHOOK ROUTER] depositId: 550e8400-..., status: COMPLETED
       [WEBHOOK ROUTER] Not found in Africa Cyber Trust DB
       [WEBHOOK ROUTER] Forwarding to Haraka...

T+10s  POST to https://harakabackend.onrender.com/api/v1/payments/webhooks/pawapay
       
       Haraka Backend:
       [PAWAPAY] Webhook received: depositId 550e8400-...
       [PAWAPAY] Order found: ORDER_12345
       [PAWAPAY] Updating order status to PAID
       [PAWAPAY] Notifying customer: Payment confirmed
       [PAWAPAY] Notifying restaurant: New order
       
       Haraka returns:
       {
         "success": true,
         "orderId": "ORDER_12345",
         "status": "PAID"
       }

T+11s  Africa Cyber Trust logs:
       [WEBHOOK ROUTER] Haraka: 200
       [WEBHOOK ROUTER] ✅ Handled by Haraka
       
       Africa Cyber Trust returns to PawaPay:
       {
         "success": true,
         "handled": true
       }

T+12s  Customer receives notification:
       "Payment confirmed! Your order is being prepared."

T+13s  Restaurant receives notification:
       "New order: ORDER_12345 - 5,000 RWF PAID"
```

---

## Code Flow

### 1. Webhook Endpoint (`payments.py:572`)
```python
@router.post("/webhooks/pawapay")
async def pawapay_webhook(
    payload: PawaPayWebhookPayload,
    db: Session = Depends(get_db)
):
    # Step 1: Check Africa Cyber Trust
    payment = db.query(Payment).filter(
        Payment.external_reference == payload.depositId
    ).first()
    
    if payment:
        # Process ACT payment
        return process_act_payment(payment, payload)
    
    # Step 2: Forward to Haraka
    haraka_result = await _forward_to_haraka(payload)
    if haraka_result["handled"]:
        return haraka_result["response"]
    
    # Step 3: Forward to EscoPay/DDA
    escopay_result = await _forward_to_escopay_dda(payload)
    if escopay_result["handled"]:
        return escopay_result["response"]
    
    # Step 4: Not found
    return {"error": "Payment not found"}
```

### 2. Haraka Forwarder (`payments.py:504`)
```python
async def _forward_to_haraka(payload: PawaPayWebhookPayload):
    haraka_url = "https://harakabackend.onrender.com/api/v1/payments/webhooks/pawapay"
    
    response = requests.post(
        haraka_url,
        json=payload.dict(),
        headers={"Content-Type": "application/json"},
        timeout=15
    )
    
    if response.status_code in [200, 201]:
        return {"handled": True, "response": response.json()}
    
    return {"handled": False}
```

---

## Benefits

### 1. **Single Integration Point**
   - One webhook URL in PawaPay dashboard
   - Manages all 4 apps automatically
   - No manual switching needed

### 2. **Automatic Routing**
   - Smart detection of which app owns the payment
   - Cascading fallback to other apps
   - Zero configuration per payment

### 3. **Centralized Logging**
   - All webhook events logged in one place
   - Easy debugging: see entire routing path
   - Clear audit trail

### 4. **Fault Tolerance**
   - If Haraka is down, tries EscoPay/DDA
   - Timeout protection (15s max per app)
   - Graceful error handling

### 5. **Scalability**
   - Easy to add new apps (just add another forwarder)
   - No changes to PawaPay configuration
   - No changes to existing app backends

---

## Monitoring Commands

### Check Africa Cyber Trust Logs:
```bash
# In Render dashboard → Logs
# Filter for:
[WEBHOOK ROUTER]

# Example output:
[WEBHOOK ROUTER] PawaPay callback - depositId: abc123, status: COMPLETED
[WEBHOOK ROUTER] Not found in Africa Cyber Trust DB - forwarding...
[WEBHOOK ROUTER] Haraka: 200
[WEBHOOK ROUTER] ✅ Handled by Haraka
```

### Check Haraka Backend Logs:
```bash
# In Haraka Render dashboard → Logs
# Filter for:
[PAWAPAY]

# Example output:
[PAWAPAY] Webhook received: depositId abc123
[PAWAPAY] Order found: ORDER_12345
[PAWAPAY] Payment confirmed
```

### Test Webhook Routing:
```bash
# Send test webhook (use PawaPay sandbox):
curl -X POST https://africa-cyber-trust.onrender.com/api/payments/webhooks/pawapay \
  -H "Content-Type: application/json" \
  -d '{
    "depositId": "test-123",
    "status": "COMPLETED",
    "amount": "5000.00",
    "currency": "RWF",
    "correspondent": "MTN_MOMO_RWA"
  }'
```

---

**Last Updated:** October 3, 2026  
**Status:** ✅ Production Ready
