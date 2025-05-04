# Session Tracking System

This project implements a session tracking system with both client-side and server-side components.

## Requirements

- Python 3.8+
- Node.js 14+ (for development tools only)

## Installation

Install Python dependencies:

```bash
pip install -r requirements.txt
```

## Running the Server

Start the FastAPI server:

```bash
python server.py
```

The server will run at http://localhost:8767.

## Features

- Session lifecycle management (start, heartbeat, and stop)
- CSRF protection
- Cross-tab communication using BroadcastChannel API
- Automatic session cleanup
- Secure cookie handling

## How It Works

### Client-Side (tracking.js)
- Detects browser tab open/close events
- Communicates with other tabs via BroadcastChannel
- Sends session requests to the server
- Manages CSRF tokens and cookies

### Server-Side (server.py)
- FastAPI application handling session requests
- Secure cookie management
- CSRF token validation
- Static file serving
