"""Test equipment list API"""
import httpx

print("Testing GET /api/equipment...")

try:
    response = httpx.get("http://localhost:8000/api/equipment", timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
    if hasattr(e, 'response'):
        print(f"Response data: {e.response.json() if e.response else 'No response'}")
