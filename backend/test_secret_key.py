"""Check SECRET_KEY"""
from app.core.config import settings
from app.core.security import create_temp_token, decode_token

print("Current SECRET_KEY:")
print(f"  {settings.SECRET_KEY[:30]}...")
print(f"  Length: {len(settings.SECRET_KEY)}")
print()

# Test creating and decoding a token
print("Testing token creation and decoding...")
test_data = {"sub": "999", "username": "test", "type": "temp"}  # sub must be string

# Create token
token = create_temp_token(test_data)
print(f"Created token: {token[:50]}...")
print()

# Decode token
decoded = decode_token(token)
if decoded:
    print("SUCCESS! Token can be created and decoded")
    print(f"  Decoded data: {decoded}")
else:
    print("FAILED! Token cannot be decoded")
    print("  This means there's an issue with JWT encoding/decoding")
