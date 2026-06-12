# How to Get Free API Keys (2 minutes each)

## 1. VirusTotal API Key (FREE - 500 requests/day)

**Step 1:** Go to https://www.virustotal.com/gui/join-us

**Step 2:** Click "Sign Up" (can use Google account)

**Step 3:** After login, go to https://www.virustotal.com/gui/my-apikey

**Step 4:** Copy your API key

**Step 5:** Add to `.env` file:
```
VIRUSTOTAL_API_KEY=your-key-here
```

---

## 2. Google Safe Browsing API Key (FREE - 10,000 requests/day)

**Step 1:** Go to https://console.cloud.google.com/

**Step 2:** Create a new project (or use existing)

**Step 3:** Enable Safe Browsing API:
- Go to https://console.cloud.google.com/apis/library/safebrowsing.googleapis.com
- Click "Enable"

**Step 4:** Create API Key:
- Go to https://console.cloud.google.com/apis/credentials
- Click "+ CREATE CREDENTIALS" → "API key"
- Copy the key

**Step 5:** Add to `.env` file:
```
GOOGLE_SAFE_BROWSING_KEY=your-key-here
```

---

## 3. Restart Backend

After adding keys to `.env`:

```bash
# Kill old backend
pkill -f uvicorn

# Start new backend
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

---

## What Works Without API Keys?

The scam detector still works with these features:
- ✅ Domain age check (WHOIS)
- ✅ WHOIS privacy detection
- ✅ SSL certificate validation
- ✅ Typosquatting detection
- ✅ Suspicious keyword detection

Adding the API keys enables:
- ⭐ VirusTotal reputation (malware/phishing blacklists)
- ⭐ Google Safe Browsing (dangerous site detection)

**Result:** Works great without keys, but 10x better with them!
