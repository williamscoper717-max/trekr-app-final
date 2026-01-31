from fastapi import FastAPI
from routers import user, code, trip, adem, program, tip
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from config import SECRET_APP_KEY
from starlette.requests import Request
from fastapi.staticfiles import StaticFiles
import os
from config import UPLOAD_DIR

# Create FastAPI instance
app = FastAPI(debug=True)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_APP_KEY
)

app.middleware("http")

os.makedirs(UPLOAD_DIR, exist_ok=True)
if os.path.exists("images"):
    app.mount("/images", StaticFiles(directory="images"), name="images")

async def debug_session(request: Request, call_next):
    print(f"Session during request: {request.session}")
    response = await call_next(request)
    return response

# Include user and trip routes
app.include_router(user.router, prefix="/users", tags=["users"])
app.include_router(code.router, prefix="/users", tags=["codes"])
app.include_router(trip.router, prefix="/trips", tags=["trips"])
app.include_router(adem.router, prefix="/adems", tags=["adems"])
app.include_router(program.router, prefix="/program", tags=["program"])
app.include_router(tip.router, prefix="/tip", tags=["tip"])
