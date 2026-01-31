from passlib.context import CryptContext
import random
from datetime import datetime, timedelta
from jose import jwt
from config import SECRET_KEY, ALGORITHM, GOOGLE_CLIENT_ID, DISTANCEMATRIX_ACCURATE_KEY
import secrets
import string
import google.auth.transport.requests
import google.oauth2.id_token
from fastapi import HTTPException, UploadFile
import requests
import httpx
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def generate_code() -> str:
     return ''.join(f"{random.randint(0, 99):02d}" for _ in range(2))

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    # expire = datetime.now() + (expires_delta if expires_delta else timedelta(days=10))
    expire = datetime.now() + timedelta(days=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def cookie_secret() -> str:
    return secrets.token_hex(32)

def generate_state(length=16):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def verify_google_token(id_token: str):
    try:
        # Use Google's public keys to verify the token
        request = google.auth.transport.requests.Request()
        id_info = google.oauth2.id_token.verify_oauth2_token(id_token, request, audience=GOOGLE_CLIENT_ID)

        # Extract user info
        return {
            "email": id_info["email"],
            "name": id_info.get("name", id_info["email"].split("@")[0]),
            "picture": id_info.get("picture")
        }

    except google.auth.exceptions.GoogleAuthError as e:
        raise HTTPException(status_code=400, detail="Invalid ID token")

def generate_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password

def get_distance_accurate(origin: str, destination: str) -> float:
    url = "https://api.distancematrix.ai/maps/api/distancematrix/json"
    params = {
        "origins": origin,
        "destinations": destination,
        "key": DISTANCEMATRIX_ACCURATE_KEY,
        "units": "metric"
    }
    response = requests.get(url, params=params)
    data = response.json()
    # print(data)
    
    if data['status'] == 'OK':
        element = data['rows'][0]['elements'][0]
        if element['status'] == 'OK':
            distance_meters = element['distance']['value']
            distance_km = distance_meters / 1000
            return distance_km
        else:
            raise ValueError(f"Distance element error: {element['status']}")
    else:
        raise ValueError(f"API error: {data['status']}")
    
def estimate_carbon_emission(origin: str, destination: str, transport_type='plane') -> float:
    distance_km = get_distance_accurate(origin, destination)
    emission_rates = {
        'plane': 0.15,
        'car': 0.12,
        'train': 0.05,
    }
    # print(emission_rates)
    return round(distance_km * emission_rates.get(transport_type, 0.15), 2)

async def my_public_ip():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.ipify.org?format=json")
        return response.json()["ip"]
    
def get_itinerary_data(transportation: str, language: str, origin: str, destination: str, budget: int, days: int, num_people: int) -> dict:
    # url = "http://64.226.86.96:8080/api/orchestrator/create_itinerary"
    # url = "http://209.38.231.73:8085/get_itinerary"
    # url = "http://127.0.0.1:8000/api/v1/create_itinerary"
    # url = "http://64.226.86.96:8081"
    # url = "http://64.226.86.96:8081/api/v1/create_itinerary"
    # url = "http://64.226.86.96:8000/api/v1/create_itinerary"
    url = "http://209.38.231.73:8000/api/v1/create_itinerary"
    
    params = {
        "location": origin,
        "destination": destination,
        "budget": budget,
        "num_days": days,
        "num_people": num_people,
        "transport_mode": transportation,
        "language": language
    }

    try:
        response = requests.post(url, json=params, timeout=15)
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        print("API error response:", response.text)
        raise
    except requests.exceptions.Timeout:
        raise TimeoutError("Request timed out after 15 seconds.")

    return response.json()

async def save_upload_file(upload_file: UploadFile, destination: str):
    os.makedirs(os.path.dirname(destination), exist_ok=True) 
    
    with open(destination, "wb") as buffer:
        while True:
            chunk = await upload_file.read(1024)
            if not chunk:
                break
            buffer.write(chunk)
    await upload_file.close()
    
def validate_itinerary_response(resp: dict):
    if not isinstance(resp, dict):
        raise ValueError("IA response is not a JSON object")

    # Support both old and new format
    if "itinerary" not in resp and not (resp.get("success") and "data" in resp):
        found_keys = list(resp.keys())
        raise ValueError(
            f"Expected key 'itinerary' or 'data' at root level, "
            f"but found keys: {found_keys}"
        )