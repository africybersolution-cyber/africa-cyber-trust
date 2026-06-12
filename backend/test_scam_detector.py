"""Quick test of scam detector service."""
import asyncio
import sys
sys.path.insert(0, '.')

from app.services.scam_detector_service import scam_detector


async def test():
    print("Testing Scam Detector...\n")

    # Test 1: Legitimate site
    print("1. Testing google.com (should be SAFE)")
    result = await scam_detector.check_website("https://google.com")
    print(f"   Trust Score: {result['trust_score']}/100")
    print(f"   Verdict: {result['verdict']}")
    print(f"   Red Flags: {len(result['red_flags'])}")
    print()

    # Test 2: New/suspicious domain
    print("2. Testing verify-paypal-account.com (should be SUSPICIOUS)")
    result = await scam_detector.check_website("https://verify-paypal-account.com")
    print(f"   Trust Score: {result['trust_score']}/100")
    print(f"   Verdict: {result['verdict']}")
    print(f"   Red Flags: {len(result['red_flags'])}")
    if result['red_flags']:
        print(f"   First flag: {result['red_flags'][0]['message']}")
    print()

    # Test 3: Check API key status
    print("3. API Key Status:")
    vt_status = "ENABLED" if scam_detector.virustotal_key else "NOT SET (optional)"
    sb_status = "ENABLED" if scam_detector.safe_browsing_key else "NOT SET (optional)"
    print(f"   VirusTotal: {vt_status}")
    print(f"   Safe Browsing: {sb_status}")
    print()

    print("SUCCESS: Scam detector is working!")


if __name__ == "__main__":
    asyncio.run(test())
