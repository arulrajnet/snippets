import os
import secrets
from datetime import datetime, timedelta
from typing import Dict

from fastapi import FastAPI, Request, Response, Cookie, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import APIKeyCookie
import uvicorn

# Constants
CSRF_COOKIE_NAME = "_my_csrf_token"
SESSION_COOKIE_NAME = "_my_session_id"
CSRF_HEADER_NAME = "X-CSRF-Token"
COOKIE_MAX_AGE = 24 * 60 * 60  # 24 hours in seconds

# Initialize FastAPI app
app = FastAPI(title="Session Tracker API")

# Store active sessions in memory (in production, use Redis or similar)
active_sessions: Dict[str, Dict] = {}

# Create APIKeyCookie for session handling
session_cookie = APIKeyCookie(name=SESSION_COOKIE_NAME, auto_error=False)
csrf_cookie = APIKeyCookie(name=CSRF_COOKIE_NAME, auto_error=False)

# Helper function to generate secure tokens
def generate_token():
    return secrets.token_urlsafe(32)

# Dependency to get and validate session
async def get_session(
    session_id: str = Depends(session_cookie),
    csrf_token: str = Depends(csrf_cookie),
):
    if not session_id or session_id not in active_sessions:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    session = active_sessions[session_id]
    if session['csrf_token'] != csrf_token:
        raise HTTPException(status_code=403, detail="CSRF token mismatch")

    return session_id

# Updated dependency to get and validate session with header-based CSRF tokens
async def get_session_with_csrf_header(
  request: Request,
  session_id: str = Depends(session_cookie),
):
  if not session_id or session_id not in active_sessions:
    raise HTTPException(status_code=401, detail="Invalid or expired session")

  session = active_sessions[session_id]

  # Check CSRF token from header first
  csrf_header = request.headers.get(CSRF_HEADER_NAME)

  # Validate CSRF token from either source
  if csrf_header:
    if session['csrf_token'] != csrf_header:
      raise HTTPException(status_code=403, detail="CSRF header token mismatch")
  else:
    raise HTTPException(status_code=403, detail="CSRF token missing")

  return session_id

# Mount static files
current_dir = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=current_dir), name="static")

# Root endpoint to serve the HTML page
@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open(os.path.join(current_dir, "index.html"), "r") as f:
        content = f.read()
    return HTMLResponse(content=content)

# Session endpoints
@app.get("/_session/start")
async def start_session(request: Request, response: Response):

    # Always generate a new CSRF token
    csrf_token = generate_token()

    # Check request for existing session cookie
    request_cookies = request.cookies
    existing_session_id = request_cookies.get(SESSION_COOKIE_NAME)

    if existing_session_id and existing_session_id in active_sessions:
      # Reuse existing session but generate new CSRF token
      session_id = existing_session_id
      active_sessions[session_id]["last_activity"] = datetime.now()
      # TODO: Maintain multiple CSRF tokens for the same session if needed
      active_sessions[session_id]["csrf_token"] = csrf_token
    else:
      # Generate new session ID if none exists or is invalid
      session_id = generate_token()

      # Store session info
      active_sessions[session_id] = {
          "csrf_token": csrf_token,
          "tracking_id": session_id,
          "created_at": datetime.now(),
          "last_activity": datetime.now(),
          "session_active": True
      }

    # Set cookies
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_id,
        httponly=True,
        max_age=COOKIE_MAX_AGE,
        samesite="lax",
        secure=True
    )

    response.set_cookie(
        key=CSRF_COOKIE_NAME,
        value=csrf_token,
        httponly=False,  # Client JS needs to access this
        max_age=COOKIE_MAX_AGE,
        samesite="lax",
        secure=True
    )

    return {"status": "success", "message": "Session started"}

@app.post("/_session/heartbeat")
async def heartbeat(
    session_id: str = Depends(get_session_with_csrf_header)
):
    # Update last activity timestamp
    if session_id in active_sessions:
        active_sessions[session_id]["last_activity"] = datetime.now()

    return {"status": "success", "message": "Heartbeat received"}

@app.post("/_session/stop")
async def stop_session(
    session_id: str = Depends(get_session_with_csrf_header),
    response: Response = None,
):
    # Remove session from active sessions
    if session_id in active_sessions:
        del active_sessions[session_id]

    # Clear cookies
    response.delete_cookie(key=SESSION_COOKIE_NAME)
    response.delete_cookie(key=CSRF_COOKIE_NAME)

    return {"status": "success", "message": "Session stopped"}

# Session cleanup task (would be better with APScheduler in production)
@app.on_event("startup")
async def setup_periodic_cleanup():
    # Here you would set up a background task to clean expired sessions
    # For simplicity, we're not implementing this in this example
    pass

# Function to clean up expired sessions
def cleanup_expired_sessions():
    current_time = datetime.now()
    expired_threshold = current_time - timedelta(hours=24)

    for session_id in list(active_sessions.keys()):
        session = active_sessions[session_id]
        if session["last_activity"] < expired_threshold:
            del active_sessions[session_id]

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8767, reload=True)
