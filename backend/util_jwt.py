
import base64, json, time, hmac, hashlib
from config import JWT_SECRET, JWT_ALGO, TOKEN_EXP_MINUTES

def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

def _b64url_decode(data: str) -> bytes:
    padding = '=' * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)

def jwt_encode(payload: dict) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    header_b64 = _b64url(json.dumps(header, separators=(",", ":"), sort_keys=True).encode())
    payload_b64 = _b64url(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode())
    signing_input = f"{header_b64}.{payload_b64}".encode()
    signature = hmac.new(JWT_SECRET.encode(), signing_input, hashlib.sha256).digest()
    signature_b64 = _b64url(signature)
    return f"{header_b64}.{payload_b64}.{signature_b64}"

def jwt_decode(token: str) -> dict:
    header_b64, payload_b64, signature_b64 = token.split(".")
    signing_input = f"{header_b64}.{payload_b64}".encode()
    signature_check = hmac.new(JWT_SECRET.encode(), signing_input, hashlib.sha256).digest()
    if _b64url(signature_check) != signature_b64:
        raise ValueError("Invalid token signature")
    payload = json.loads(_b64url_decode(payload_b64))
    if "exp" in payload and time.time() > payload["exp"]:
        raise ValueError("Token expired")
    return payload

def make_demo_token(username: str = "admin"):
    now = int(time.time())
    exp = now + TOKEN_EXP_MINUTES * 60
    payload = {"sub": username, "role": "admin", "iat": now, "exp": exp}
    return jwt_encode(payload)
