""
Security middleware for adding security headers and rate limiting.
"""
from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.rate_limits = {}
        self.RATE_LIMIT = 100  # Requests
        self.RATE_LIMIT_WINDOW = 60  # Seconds

    async def dispatch(self, request: Request, call_next):
        # Rate limiting
        client_ip = request.client.host
        current_time = time.time()
        
        # Clean up old entries
        self.rate_limits = {
            ip: (count, timestamp) 
            for ip, (count, timestamp) in self.rate_limits.items()
            if current_time - timestamp < self.RATE_LIMIT_WINDOW
        }
        
        # Check rate limit
        if client_ip in self.rate_limits:
            count, timestamp = self.rate_limits[client_ip]
            if count >= self.RATE_LIMIT:
                return Response(
                    content={"detail": "Rate limit exceeded"},
                    status_code=429,
                    headers={"Retry-After": str(self.RATE_LIMIT_WINDOW)}
                )
            self.rate_limits[client_ip] = (count + 1, current_time)
        else:
            self.rate_limits[client_ip] = (1, current_time)
        
        # Process request
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:;"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response

def setup_cors(app):
    """Configure CORS with secure defaults."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],  # Update with your frontend URL
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["Content-Range", "X-Total-Count"],
        max_age=600,  # 10 minutes
    )
    return app
