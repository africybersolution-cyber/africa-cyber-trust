# Pricing System Implementation Plan

## 📊 Current State Analysis

### ✅ What Already Exists:

1. **Database Models** (`app/models/subscription.py`):
   - `Subscription` - Tracks user subscriptions
   - `Payment` - Payment transactions
   - `ServiceUsage` - Billing tracking
   - Trial system fields in User model

2. **Payment Integration** (`app/api/payments.py`):
   - PawaPay mobile money (19 African countries)
   - Currency conversion for local pricing
   - Payment status checking
   - Subscription creation/extension

3. **Pricing Service** (`app/services/pricing_service.py`):
   - Multi-country pricing (20 countries)
   - Operator mapping (MTN, Airtel, M-Pesa, etc.)
   - Current plans: "personal" (~$5) and "business" (~$15)

4. **Frontend** (`app/pricing/page.tsx`):
   - 3-tier pricing (Free, Professional $99, Enterprise $499)
   - Monthly/Annual toggle
   - 14-day trial mentioned

### ❌ What's Missing:

1. **Crypto Payment Integration**:
   - No USDT/USDC payment option
   - Need to add Polygon blockchain integration

2. **Plan Mismatch**:
   - Backend: personal ($5), business ($15)
   - Frontend: Free, Professional ($99), Enterprise ($499)
   - User wants: Personal ($5), Professional ($49), Enterprise (custom)

3. **Trial System**:
   - Fields exist but not fully integrated
   - Need 7-day trial for Personal
   - Need 14-day trial for Professional

4. **Access Control**:
   - Personal users should only access home page features
   - Professional users get full dashboard
   - Not currently enforced

---

## 🎯 New Requirements

### Three-Tier Pricing:

| Tier | Price | Trial | Features |
|------|-------|-------|----------|
| **Personal** | $5/month | 7 days | Unlimited home page scans (scam detection, AI photo/video), scan history |
| **Professional** | $49/month | 14 days | Everything in Personal + Full dashboard + Vulnerability scanning + Alerts + Reports + 5 team members |
| **Enterprise** | Custom | Negotiable | Everything in Professional + Dedicated analyst + Custom integrations + SLA + Unlimited team |

### Payment Methods:
1. **Mobile Money** (PawaPay) - Already working ✅
2. **Crypto** (USDT/USDC on Polygon) - Need to add ❌

---

## 🛠️ Implementation Steps

### Phase 1: Update Pricing Data (30 mins)

**Files to modify:**
1. `backend/app/services/pricing_service.py`
   - Change "business" to "professional"
   - Update prices from ~$15 to ~$49 equivalent
   - Add "enterprise" placeholder

2. `frontend/app/pricing/page.tsx`
   - Remove "Free" tier
   - Change "Professional" from $99 to $49
   - Update "Personal" to show $5
   - Update trial periods (7 days for Personal, 14 for Professional)

**Testing:**
- Check pricing page renders correctly
- Verify prices match across tiers

---

### Phase 2: Trial System (1 hour)

**Files to modify:**
1. `backend/app/services/trial_service.py` (check if exists, create if not)
   - 7-day trial for Personal
   - 14-day trial for Professional
   - Auto-expire logic

2. `backend/app/api/auth.py` (registration)
   - Set trial_started_at on signup
   - Set trial_ends_at based on plan
   - Set trial_status = 'active'

**Testing:**
- Create new account
- Verify trial dates set correctly
- Check trial expiration after period

---

### Phase 3: Access Control (1 hour)

**Files to modify:**
1. `backend/app/api/auth.py`
   - Add middleware to check subscription status
   - Personal users: only home page API access
   - Professional users: full dashboard access

2. `frontend/app/dashboard/layout.tsx`
   - Check user subscription
   - Redirect Personal users to limited view
   - Show upgrade prompt if needed

**Testing:**
- Personal user tries to access dashboard → blocked or limited
- Professional user accesses all features
- Trial expired user → payment prompt

---

### Phase 4: Crypto Payment Integration (2 hours)

**Files to create/modify:**
1. `backend/app/services/crypto_payment_service.py` (NEW)
   - Copy from EscoPay project
   - Web3 integration for Polygon
   - USDT/USDC contract interaction
   - Payment verification

2. `backend/app/api/payments.py`
   - Add `/initiate-crypto` endpoint
   - Accept wallet address
   - Generate payment request
   - Verify on-chain payment

3. `frontend/components/PaymentModal.tsx` (NEW)
   - Mobile Money option (existing)
   - Crypto option (new)
   - MetaMask integration
   - Payment confirmation

**Dependencies:**
```bash
pip install web3
npm install ethers
```

**Testing:**
- Test USDT payment on Polygon testnet
- Verify payment confirmation
- Check subscription activation

---

### Phase 5: Update Backend API (1 hour)

**Files to modify:**
1. `backend/app/api/public_check.py`
   - Check user subscription status
   - Free users: 1 scan per day (IP-based)
   - Personal users: unlimited scans (requires login)
   - Professional users: unlimited + dashboard

2. `backend/app/models/subscription.py`
   - Add trial_days field
   - Update plan_name enum ('personal', 'professional', 'enterprise')

**Testing:**
- Free user (no account): 1 scan per day
- Personal user (paid): unlimited scans
- Professional user: unlimited + dashboard access

---

### Phase 6: Frontend Updates (2 hours)

**Files to create/modify:**
1. `frontend/app/signup/page.tsx`
   - Plan selection during signup
   - Start trial immediately
   - Payment after trial or during trial

2. `frontend/app/dashboard/billing/page.tsx` (NEW)
   - Current plan display
   - Trial countdown
   - Upgrade/downgrade options
   - Payment history
   - Add payment method

3. `frontend/components/UpgradePrompt.tsx` (NEW)
   - Show when Personal user tries Professional feature
   - Payment modal

**Testing:**
- Signup flow with plan selection
- Trial activation
- Payment after trial
- Upgrade path

---

## 📝 Pricing Table (Multi-Currency)

### Current Backend Pricing:
```
Personal  ~$5  USD equivalent
Business  ~$15 USD equivalent
```

### New Pricing Needed:
```
Personal      ~$5   USD equivalent ✅ (keep as is)
Professional  ~$49  USD equivalent ❌ (update from $15)
Enterprise    Custom (contact sales)
```

### Example Updated Prices:

| Country | Currency | Personal | Professional |
|---------|----------|----------|--------------|
| Rwanda | RWF | 25,000 | 245,000 |
| Kenya | KES | 2,500 | 24,500 |
| Uganda | UGX | 70,000 | 686,000 |
| Tanzania | TZS | 45,000 | 441,000 |
| Ghana | GHS | 300 | 2,940 |
| South Africa | ZAR | 350 | 3,430 |

*(Formula: Professional = Personal × 9.8)*

---

## 🚀 Quick Start Implementation

**Recommended Order:**
1. ✅ Phase 1: Update pricing (easy, visible change)
2. ✅ Phase 2: Trial system (core functionality)
3. ✅ Phase 5: Backend API updates (access control)
4. ✅ Phase 6: Frontend updates (user experience)
5. ✅ Phase 3: Access control enforcement
6. ✅ Phase 4: Crypto payment (bonus feature)

**Total Estimated Time:** 7-8 hours

---

## ✅ Testing Checklist

### Pricing Page:
- [ ] Three tiers display correctly
- [ ] Prices match backend
- [ ] Trial periods shown (7 days Personal, 14 days Professional)
- [ ] CTA buttons link correctly

### Signup Flow:
- [ ] Can select plan during signup
- [ ] Trial starts automatically
- [ ] Trial dates set in database

### Trial System:
- [ ] Trial countdown visible
- [ ] Trial expires after period
- [ ] Payment prompt shows on expiry

### Access Control:
- [ ] Free user: 1 scan/day (IP-based)
- [ ] Personal user: unlimited scans, no dashboard
- [ ] Professional user: unlimited scans + full dashboard

### Payments:
- [ ] Mobile money works (PawaPay)
- [ ] Crypto works (USDT/USDC)
- [ ] Subscription activates after payment
- [ ] Payment history saved

### Upgrade/Downgrade:
- [ ] Can upgrade Personal → Professional
- [ ] Prorated billing works
- [ ] Immediate access after upgrade

---

## 🔒 Security Considerations

1. **Trial Abuse Prevention**:
   - One trial per email
   - Track by email + phone number
   - IP tracking for free tier

2. **Payment Verification**:
   - PawaPay: webhook callback
   - Crypto: on-chain verification
   - Never trust client-side

3. **Access Control**:
   - Server-side subscription checks
   - Middleware on all dashboard routes
   - Rate limiting on API endpoints

---

**Ready to start implementation?**
