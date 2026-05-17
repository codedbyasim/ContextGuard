import os
import jwt
from dotenv import load_dotenv

load_dotenv("backend/.env")
secret = os.getenv("JWT_SECRET_KEY")
print(f"Loaded Secret: {secret[:10]}...")

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Indma2lsaHdnaGRrZGR4Z2NsanlxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg5ODU4MTcsImV4cCI6MjA5NDU2MTgxN30.zW2yMzy8_-iqEL3Z4iQJ5-Y4FSTxjZ3yj7thNmhucl4"

try:
    # Decode without verifying audience
    payload = jwt.decode(token, secret, algorithms=["HS256"], options={"verify_audience": False})
    print("SUCCESS! Payload:", payload)
except Exception as e:
    print("FAILED! Error:", type(e).__name__, str(e))
