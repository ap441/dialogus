# Google OAuth Setup Guide

This guide explains how to configure Google Sign-In for Dialogus.

## Prerequisites

1. A Google Cloud Project
2. The Dialogus backend and frontend dependencies installed

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the "Google+ API"

## Step 2: Create OAuth 2.0 Credentials

1. Go to **Credentials** in the left sidebar
2. Click **Create Credentials** → **OAuth 2.0 Client ID**
3. You may need to configure the OAuth consent screen first:
   - User Type: External
   - Add required scopes: `email`, `profile`, `openid`
   - Add test users if desired
4. For Application Type, select **Web application**
5. Under **Authorized JavaScript origins**, add:
   - `http://localhost:3000`
   - `http://localhost` (for testing)
   - Your production domain (e.g., `https://dialogus.example.com`)
6. Under **Authorized redirect URIs**, add:
   - `http://localhost:3000/home` (or any route that handles login)
7. Copy the **Client ID** (you'll need this)

## Step 3: Set Environment Variables

### Backend (Python)

Create a `.env` file in the `backend/` directory or set the environment variable:

```bash
export GOOGLE_CLIENT_ID="your-client-id-here.apps.googleusercontent.com"
```

Or pass it when running:

```bash
GOOGLE_CLIENT_ID="your-client-id-here.apps.googleusercontent.com" uvicorn app.main:app --reload
```

### Frontend (Next.js)

Create a `.env.local` file in the `frontend/` directory:

```
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
```

## Step 4: Install Dependencies

### Backend

```bash
cd backend
pip install -r requirements.txt
```

### Frontend

```bash
cd frontend
npm install
```

## Step 5: Run the Application

### Backend

```bash
cd backend
GOOGLE_CLIENT_ID="your-client-id-here.apps.googleusercontent.com" uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm run dev
```

## Step 6: Test Google Sign-In

1. Navigate to `http://localhost:3000/login` or `http://localhost:3000/signup`
2. Click the **Google Sign-In** button
3. Follow the Google login flow
4. You should be logged in and redirected to `/home`

## How It Works

### Backend Flow

1. Frontend sends the Google ID token to `/api/auth/google`
2. Backend verifies the token using Google's public keys
3. Backend extracts email and name from the token
4. Backend finds or creates a user with that email
5. Backend issues a JWT token for the application
6. Frontend stores the JWT and uses it for subsequent requests

### Frontend Flow

1. User clicks the Google Sign-In button
2. Google OAuth popup opens
3. User authenticates with Google
4. Frontend receives an ID token
5. Frontend sends the token to `/api/auth/google`
6. Backend verifies and returns a JWT
7. Frontend stores the JWT and redirects to `/home`

## Troubleshooting

### "Google OAuth not configured"

Make sure `GOOGLE_CLIENT_ID` environment variable is set on the backend.

### "Invalid token" error

- Check that your Client ID matches between frontend and backend
- Verify that your domain is in the authorized JavaScript origins
- Make sure the token hasn't expired (tokens are typically valid for 1 hour)

### CORS errors

If you get CORS errors, ensure:
- Backend has the correct `CORS_ORIGINS` set
- Frontend is making requests to the correct backend URL

Example:
```bash
CORS_ORIGINS="http://localhost:3000" GOOGLE_CLIENT_ID="your-id" uvicorn app.main:app --reload
```

### Token verification fails

- Ensure `google-auth==2.29.0` is installed (run `pip install -r requirements.txt`)
- Double-check the Client ID in both frontend and backend
