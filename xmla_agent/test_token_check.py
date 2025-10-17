"""
Test Token Validity Check
==========================
This script tests the check_token_validity() function to verify
it correctly detects whether a cached authentication token exists.
"""

from get_token import check_token_validity

def test_token_check():
    """Test the token validity check function."""
    print("=" * 70)
    print("Testing Token Validity Check")
    print("=" * 70)
    print("\nChecking for cached authentication token...")

    result = check_token_validity()

    print("\n" + "-" * 70)
    print("Results:")
    print("-" * 70)
    print(f"Valid Token Exists:    {result['valid']}")
    print(f"Requires Auth:         {result['requires_auth']}")
    print(f"Account:               {result.get('account', 'N/A')}")

    if 'error' in result:
        print(f"Error:                 {result['error']}")

    print("-" * 70)

    # Interpret results
    print("\nInterpretation:")
    if result['valid']:
        print("[PASS] Valid cached token found")
        print("  You can proceed with data context agent without authentication")
        print(f"  Authenticated as: {result.get('account', 'Unknown')}")
    elif result['requires_auth']:
        print("[WARN] Authentication required")
        print("  No valid cached token found")
        print("  You need to authenticate before using the data context agent")
        if result.get('account'):
            print(f"  Previous account: {result['account']} (token expired)")
    else:
        print("[UNKNOWN] Unexpected status")

    print("\n" + "=" * 70)
    return result

if __name__ == "__main__":
    test_token_check()
