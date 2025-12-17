import os
import sys
import requests

def test_health():
    try:
        response = requests.get('http://127.0.0.1:5000/api/health')
        if response.status_code == 200:
            print("✅ Server is running and healthy.")
            return True
        else:
            print(f"❌ Server returned status code {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Is it running?")
        return False

if __name__ == "__main__":
    print("Verifying fix...")
    if test_health():
        print("\nTo verify the PDF fix fully:")
        print("1. Ensure the backend is running (python backend/app.py)")
        print("2. Upload 'Atmapur.pdf' via the Frontend or API")
        print("3. Check logs for 'Processing PDF with PyMuPDF' and 'OCR completed'")
