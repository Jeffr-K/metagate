from datetime import datetime, timedelta, UTC
from enum import Enum

from jose import jwt, ExpiredSignatureError, JWTError
from loguru import logger
import os

class TokenType(Enum):
    ACCESS = "access"
    REFRESH = "refresh"


class Token:
    SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
    ALGORITHM = "HS512"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    REFRESH_TOKEN_EXPIRE_DAYS = 7

    @staticmethod
    def generate(email: str, token_type: TokenType = TokenType.ACCESS) -> str:
        try:
            now = datetime.now(UTC)

            match token_type:
                case TokenType.ACCESS:
                    expire = now + timedelta(minutes=Token.ACCESS_TOKEN_EXPIRE_MINUTES)
                case TokenType.REFRESH:
                    expire = now + timedelta(days=Token.REFRESH_TOKEN_EXPIRE_DAYS)
                case _:
                    raise ValueError("token_type must be 'access' or 'refresh'")

            payload = {
                "sub": email,
                "email": email,
                "type": token_type.value,
                "iat": now,
                "exp": expire
            }

            token = jwt.encode(payload, Token.SECRET_KEY, algorithm=Token.ALGORITHM)
            return token
        except Exception as e:
            raise Exception(f"Token generation failed: {str(e)}")


    @staticmethod
    def verify(token: str) -> dict:
        try:
            payload = jwt.decode(token, Token.SECRET_KEY, algorithms=[Token.ALGORITHM])
            return payload
        except ExpiredSignatureError:
            raise Exception("Token has expired")
        except JWTError:
            raise Exception("Invalid token")

    @staticmethod
    def is_token_expired(token: str) -> bool:
        try:
            payload = jwt.decode(token, Token.SECRET_KEY, algorithms=[Token.ALGORITHM])
            exp = payload.get("exp")
            if exp:
                return datetime.utcnow() > datetime.fromtimestamp(exp)
            return True
        except Exception as e:
            logger.error(f"Token expiration failed: {str(e)}")
            return True

    @staticmethod
    def get_user_from_token(token: str) -> str:
        payload = Token.verify(token)
        return payload.get("email")