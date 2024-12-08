# JWKS Server

A secure JWKS server with enhanced functionality for user management and logging.

## Features
- AES-encrypted private key storage
- User registration with hashed passwords
- Authentication logging
- Rate limiting to prevent abuse

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Initialize the database: `python db_setup.py`
3. Run the server: `python server.py`

## Endpoints
- `POST /register`: Registers a user.
- `POST /auth`: Authenticates a user.
