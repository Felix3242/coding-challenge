from fastapi import HTTPException
from clerk_backend_api import Clerk, AuthenticateRequestOptions
import os
from dotenv import load_dotenv

# looking for envrionment file and environemt variables, giving us access to it
load_dotenv()

clerk_sdk = Clerk(bearer_auth=os.getenv("CLERK_SECRET_KEY"))

def authenticate_and_get_user_details(request):
    try:
        request_state = clerk_sdk.authenticate_request(
            request,
            AuthenticateRequestOptions(
                authorized_parties=["http://localhost:5173", "http://localhost:5174"],
                jwt_key=os.getenv("JWT_KEY") #makes it happen serverless, if its commented out then it actualyl sends the request and makes it slower
            )
        )
        if not request_state.is_signed_in:
            raise HTTPException(status_code=401, detail="Invalid token")

        payload = request_state.payload
        if payload is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        user_id = payload.get("sub")
        return {"user_id": user_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))