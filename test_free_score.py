"""Quick test for Free Trust Score API."""
import asyncio
import sys
sys.path.insert(0, 'C:/Users/Admin/africa-cyber-trust/backend')

from app.api.free_trust_score import _extract_domain, _calculate_score


def test_domain_extraction():
    """Test domain extraction from various inputs."""
    print("Testing domain extraction...")

    test_cases = [
        ("https://example.com", "example.com"),
        ("http://www.example.com", "example.com"),
        ("example.com", "example.com"),
        ("www.example.com", "example.com"),
        ("https://subdomain.example.com", "subdomain.example.com"),
        ("invalid", None),
        ("x.y", None),  # Too short
    ]

    passed = 0
    for input_url, expected in test_cases:
        result = _extract_domain(input_url)
        status = "PASS" if result == expected else "FAIL"
        print(f"[{status}] {input_url} -> {result} (expected: {expected})")
        if result == expected:
            passed += 1

    print(f"\nDomain extraction: {passed}/{len(test_cases)} passed\n")


def test_score_calculation():
    """Test score calculation logic."""
    print("Testing score calculation...")

    # Perfect score scenario
    perfect_checks = {
        "ssl": {"status": "pass"},
        "headers": {"status": "pass"},
        "dns": {"status": "pass"},
        "https_redirect": {"status": "pass"},
        "mixed_content": {"status": "pass"}
    }

    result = _calculate_score(perfect_checks)
    print(f"Perfect checks: Score={result['score']}, Grade={result['grade']}")
    assert result['score'] == 100, f"Expected 100, got {result['score']}"
    assert result['grade'] == "A+", f"Expected A+, got {result['grade']}"

    # Failed SSL (critical)
    failed_ssl = perfect_checks.copy()
    failed_ssl["ssl"] = {"status": "fail"}
    result = _calculate_score(failed_ssl)
    print(f"Failed SSL: Score={result['score']}, Grade={result['grade']}")
    assert result['score'] == 60, f"Expected 60 (100-40), got {result['score']}"

    # All failed
    all_failed = {
        "ssl": {"status": "fail"},
        "headers": {"status": "fail"},
        "dns": {"status": "fail"},
        "https_redirect": {"status": "fail"},
        "mixed_content": {"status": "fail"}
    }
    result = _calculate_score(all_failed)
    print(f"All failed: Score={result['score']}, Grade={result['grade']}, Critical={result['critical']}")
    assert result['score'] == 0, f"Expected 0, got {result['score']}"
    assert result['grade'] == "F", f"Expected F, got {result['grade']}"
    assert result['critical'] == 2, f"Expected 2 critical (SSL + mixed content)"

    print("\nAll score calculations passed!\n")


if __name__ == "__main__":
    test_domain_extraction()
    test_score_calculation()
    print("SUCCESS: All tests passed!")
