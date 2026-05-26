import urllib.parse
import requests

def get_google_auth_url(client_id, redirect_uri):
    """Generates the Google OAuth2 authorization URL."""
    base_url = "https://accounts.google.com/o/oauth2/v2/auth"
    params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": "openid email profile",
        "access_type": "online",
        "prompt": "select_account"
    }
    return f"{base_url}?{urllib.parse.urlencode(params)}"

def get_user_info(code, client_id, client_secret, redirect_uri):
    """Exchanges auth code for token, then fetches user profile info."""
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code"
    }
    try:
        # 1. Get access token
        r = requests.post(token_url, data=data)
        if r.status_code != 200:
            print("Token exchange failed:", r.text)
            return None
        
        token = r.json().get("access_token")
        if not token:
            return None
            
        # 2. Get user info
        userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        headers = {"Authorization": f"Bearer {token}"}
        r2 = requests.get(userinfo_url, headers=headers)
        if r2.status_code != 200:
            print("User info fetch failed:", r2.text)
            return None
            
        return r2.json()  # Returns dict with 'email', 'name', 'picture'
    except Exception as e:
        print("OAuth Exception:", str(e))
        return None
