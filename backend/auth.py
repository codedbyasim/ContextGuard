"""
ContextGuard — Dashboard user authentication (Supabase JWT).
"""

import os
import re
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from jwt import PyJWKClient

# Global JWK Client cache to optimize performance
_jwk_client = None

def get_supabase_project_ref() -> str:
    """Extracts the Supabase project reference dynamically from the DATABASE_URL."""
    db_url = os.getenv("DATABASE_URL", "")
    match = re.search(r"postgres\.([a-zA-Z0-9]+)", db_url)
    if match:
        return match.group(1)
    # Safe default fallback for your active project
    return "wfkilhwghdkddxgcljyq"

def get_jwk_client() -> PyJWKClient:
    """Gets or initializes the PyJWKClient using the public JWKS endpoint."""
    global _jwk_client
    if _jwk_client is None:
        project_ref = get_supabase_project_ref()
        jwks_url = f"https://{project_ref}.supabase.co/auth/v1/.well-known/jwks.json"
        _jwk_client = PyJWKClient(jwks_url)
    return _jwk_client

def get_jwt_secret() -> str:
    """Gets the legacy symmetric JWT secret key from environment variables."""
    secret = os.getenv("JWT_SECRET_KEY", "").strip()
    if secret:
        return secret
    return "contextguard-dev-secret-change-in-production"

def decode_access_token(token: str) -> Optional[dict]:
    """
    Decodes the Supabase JWT using a hybrid approach:
    - Symmetrically verifies HS256 using JWT_SECRET_KEY
    - Asymmetrically verifies modern ES256/RS256 using Supabase public JWKS endpoint
    """
    try:
        # Detect token signature algorithm from header
        header = jwt.get_unverified_header(token)
        alg = header.get("alg", "HS256")
        
        if alg == "HS256":
            # Legacy symmetric signature verification
            payload = jwt.decode(
                token, 
                get_jwt_secret(), 
                algorithms=["HS256"], 
                audience="authenticated"
            )
        else:
            # Modern asymmetric signature verification (ES256, RS256, etc.)
            jwk_client = get_jwk_client()
            signing_key = jwk_client.get_signing_key_from_jwt(token)
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=[alg],
                audience="authenticated"
            )
            
        user_id = payload.get("sub")
        email = payload.get("email")
        if not user_id:
            return None
        return {"id": user_id, "email": email}
    except jwt.PyJWTError as e:
        print("🔴 JWT DECODE ERROR:", str(e))
        return None
