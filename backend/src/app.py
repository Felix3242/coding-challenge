from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import challenge, webhooks

app = FastAPI()

# set this to the local port or something else to make it more secure
# uses * rn to avoid errors
# could change it to localhost5173
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(challenge.router, prefix="/api")
app.include_router(webhooks.router, prefix="/webhooks")