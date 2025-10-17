"""
Get Azure AD Access Token for Power BI XMLA
============================================
This script acquires an Azure AD token for authenticating to Power BI XMLA endpoint.
"""

import msal
import sys
import os
import atexit

# Power BI XMLA resource ID
RESOURCE = "https://analysis.windows.net/powerbi/api"

# Public client app ID for Power BI
CLIENT_ID = "ea0616ba-638b-4df5-95b9-636659ae5121"  # Power BI public client

# Authority
AUTHORITY = "https://login.microsoftonline.com/organizations"

# Token cache file location
CACHE_FILE = os.path.join(os.path.dirname(__file__), ".msal_token_cache.bin")


def load_token_cache():
    """Load token cache from disk if it exists."""
    cache = msal.SerializableTokenCache()
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            cache.deserialize(f.read())
    return cache


def save_token_cache(cache):
    """Save token cache to disk."""
    if cache.has_state_changed:
        with open(CACHE_FILE, "w") as f:
            f.write(cache.serialize())


def check_token_validity():
    """
    Check if a valid cached token exists without triggering authentication flow.

    Returns:
        dict: Status dictionary with the following structure:
            - 'valid': bool - True if valid token exists, False otherwise
            - 'requires_auth': bool - True if authentication is needed
            - 'account': str or None - Account identifier if token exists
    """
    # Check if cache file exists
    if not os.path.exists(CACHE_FILE):
        return {
            'valid': False,
            'requires_auth': True,
            'account': None
        }

    try:
        # Load token cache from disk
        cache = load_token_cache()

        # Create a public client application with token cache
        app = msal.PublicClientApplication(
            client_id=CLIENT_ID,
            authority=AUTHORITY,
            token_cache=cache
        )

        # Define the scopes (permissions) we need
        scopes = [f"{RESOURCE}/.default"]

        # Check for cached accounts
        accounts = app.get_accounts()
        if not accounts:
            return {
                'valid': False,
                'requires_auth': True,
                'account': None
            }

        # Try to get token silently from cache
        result = app.acquire_token_silent(scopes, account=accounts[0])

        if result and "access_token" in result:
            # Valid token exists, save cache in case it was refreshed
            save_token_cache(cache)
            return {
                'valid': True,
                'requires_auth': False,
                'account': accounts[0].get("username", "Unknown")
            }
        else:
            # Token expired or invalid
            return {
                'valid': False,
                'requires_auth': True,
                'account': accounts[0].get("username", "Unknown")
            }

    except Exception as e:
        # Error checking token - assume auth required
        return {
            'valid': False,
            'requires_auth': True,
            'account': None,
            'error': str(e)
        }


def get_access_token(return_flow_on_timeout=False, wait_for_user=True):
    """
    Get access token using device code flow (interactive browser authentication).
    Uses persistent token cache to avoid re-authentication on subsequent runs.

    Args:
        return_flow_on_timeout: If True, return auth flow details instead of None on failure
        wait_for_user: If False, don't wait for user authentication - return immediately with flow details

    Returns:
        str: Access token if successful
        dict: Auth flow details if return_flow_on_timeout=True and auth failed
        None: If authentication failed and return_flow_on_timeout=False
    """
    # Load token cache from disk
    cache = load_token_cache()

    # Create a public client application with token cache
    app = msal.PublicClientApplication(
        client_id=CLIENT_ID,
        authority=AUTHORITY,
        token_cache=cache
    )

    # Register callback to save cache on exit
    atexit.register(lambda: save_token_cache(cache))

    # Define the scopes (permissions) we need
    scopes = [f"{RESOURCE}/.default"]

    # First, try to get token silently from cache
    accounts = app.get_accounts()
    if accounts:
        print("\n" + "="*70)
        print("Checking for cached token...")
        print("="*70)
        result = app.acquire_token_silent(scopes, account=accounts[0])
        if result and "access_token" in result:
            print("[SUCCESS] Using cached token (no authentication required)")
            print("="*70)
            # Save cache in case token was refreshed
            save_token_cache(cache)
            return result["access_token"]
        else:
            print("Cached token expired or unavailable, re-authenticating...")

    # No cached token available, need device code flow
    print("\n" + "="*70)
    print("Azure AD Authentication Required")
    print("="*70)
    print("\nAttempting to get access token for Power BI XMLA endpoint...")
    print("You will need to authenticate via your browser.\n")

    # Try to get token using device code flow
    flow = app.initiate_device_flow(scopes=scopes)

    if "user_code" not in flow:
        raise ValueError("Failed to create device flow")

    print(flow["message"])
    sys.stdout.flush()

    # If caller doesn't want to wait (e.g., when called from automation), return flow details immediately
    if not wait_for_user:
        print("\n[WARNING] Not waiting for authentication (non-interactive mode)")
        print("Returning flow details for external handling...")
        if return_flow_on_timeout:
            return {
                'status': 'auth_required',
                'user_code': flow.get('user_code'),
                'device_code': flow.get('device_code'),
                'verification_uri': flow.get('verification_uri'),
                'expires_in': flow.get('expires_in'),
                'message': flow.get('message'),
                'error': 'auth_pending',
                'error_description': 'Authentication flow initiated but not waiting for completion (non-interactive mode)'
            }
        return None

    # Wait for user to authenticate (blocking call)
    result = app.acquire_token_by_device_flow(flow)

    if "access_token" in result:
        print("\n" + "="*70)
        print("Authentication successful!")
        print("="*70)
        # Save the token cache for next time
        save_token_cache(cache)
        return result["access_token"]
    else:
        print("\n" + "="*70)
        print("Authentication failed!")
        print("="*70)
        print(f"Error: {result.get('error')}")
        print(f"Description: {result.get('error_description')}")

        # If requested, return flow details for retry
        if return_flow_on_timeout:
            return {
                'status': 'auth_required',
                'user_code': flow.get('user_code'),
                'device_code': flow.get('device_code'),
                'verification_uri': flow.get('verification_uri'),
                'expires_in': flow.get('expires_in'),
                'message': flow.get('message'),
                'error': result.get('error'),
                'error_description': result.get('error_description')
            }

        return None


if __name__ == "__main__":
    token = get_access_token()
    if token:
        print(f"\nAccess Token (first 50 chars): {token[:50]}...")
        print("\nYou can use this token to connect to XMLA endpoint.")
    else:
        print("\nFailed to get access token.")
        sys.exit(1)
