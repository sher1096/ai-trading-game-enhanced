"""
Check which routes are available on the running Flask server
"""
import requests

try:
    # Try to access the /coins-management route
    response = requests.get('http://localhost:5000/coins-management', timeout=2)
    print(f"GET /coins-management: {response.status_code}")

    if response.status_code == 200:
        print("  [OK] Route is available")
    elif response.status_code == 404:
        print("  [ERROR] Route not found - server running old code")
        print("\n  Solution: The running Flask server was started before")
        print("  the /coins-management route was added to app.py.")
        print("\n  To fix: Kill all Python processes and restart the server.")

    # Test the API routes to confirm server is running
    response = requests.get('http://localhost:5000/api/coins', timeout=2)
    print(f"\nGET /api/coins: {response.status_code}")
    if response.status_code == 200:
        print(f"  [OK] Server is running and API works")

except Exception as e:
    print(f"[ERROR] Could not connect to server: {e}")
