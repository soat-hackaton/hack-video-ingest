import os
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Define que a API espera um Bearer Token
security_scheme = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)):
    """
    Dependência que valida o JWT Token.
    Se o token for inválido ou expirado, lança 401.
    """
    token = credentials.credentials
    secret = os.getenv("JWT_SECRET")

    if not secret:
        # Fallback seguro ou erro de configuração
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="JWT_SECRET não configurada no servidor"
        )

    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user_email(payload: dict = Depends(verify_token)) -> str:
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Token inválido: Email ausente")
    return email