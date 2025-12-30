"""Test temp token decoding"""
from app.core.security import decode_token
from datetime import datetime

# Recent temp token from login
temp_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsInVzZXJuYW1lIjoiYWRtaW4iLCJ0eXBlIjoidGVtcCIsImV4cCI6MTc2NzA2ODE3MSwiaWF0IjoxNzY3MDY3ODcxfQ.1rfmGNANRdaTx4Bp5MMLp9bammcD2L9vCpiZm5AyX40"

print("Testing temp token decoding...")
print(f"Token: {temp_token[:50]}...")
print()

payload = decode_token(temp_token)

if payload:
    print("SUCCESS! Token decoded successfully!")
    print(f"   sub (user_id): {payload.get('sub')}")
    print(f"   username: {payload.get('username')}")
    print(f"   type: {payload.get('type')}")
    print(f"   exp (expiry): {payload.get('exp')}")
    print(f"   iat (issued): {payload.get('iat')}")
    print()

    # Check if expired
    exp_timestamp = payload.get('exp')
    now_timestamp = int(datetime.utcnow().timestamp())

    print(f"   Current time: {now_timestamp}")
    print(f"   Token expires: {exp_timestamp}")

    if exp_timestamp < now_timestamp:
        print("   WARNING: TOKEN EXPIRED!")
        print(f"   Expired {now_timestamp - exp_timestamp} seconds ago")
    else:
        print(f"   OK: Token still valid ({exp_timestamp - now_timestamp} seconds remaining)")
else:
    print("FAILED! Token decoding failed!")
