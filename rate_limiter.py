"""Rate limiting middleware for API."""

import time
from typing import Dict, Tuple
from fastapi import Request, HTTPException, status
from collections import defaultdict
from datetime import datetime, timedelta


class RateLimiter:
    """Token bucket rate limiter."""
    
    def __init__(self, requests_per_minute: int = 60, burst: int = 10):
        """Initialize rate limiter.
        
        Args:
            requests_per_minute: Maximum requests per minute
            burst: Maximum burst size
        """
        self.rate = requests_per_minute / 60.0  # requests per second
        self.burst = burst
        self.buckets: Dict[str, Tuple[float, float]] = {}  # {key: (tokens, last_update)}
    
    def _get_tokens(self, key: str) -> float:
        """Get current token count for a key."""
        if key not in self.buckets:
            self.buckets[key] = (self.burst, time.time())
            return self.burst
        
        tokens, last_update = self.buckets[key]
        now = time.time()
        elapsed = now - last_update
        
        # Add tokens based on elapsed time
        tokens = min(self.burst, tokens + elapsed * self.rate)
        self.buckets[key] = (tokens, now)
        
        return tokens
    
    def _consume_token(self, key: str) -> bool:
        """Try to consume a token."""
        tokens = self._get_tokens(key)
        
        if tokens >= 1.0:
            self.buckets[key] = (tokens - 1.0, time.time())
            return True
        
        return False
    
    async def check_rate_limit(self, request: Request, user_id: str):
        """Check if request is within rate limit."""
        key = f"{user_id}:{request.url.path}"
        
        if not self._consume_token(key):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later.",
                headers={"Retry-After": "60"}
            )


class SlidingWindowRateLimiter:
    """Sliding window rate limiter."""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        """Initialize sliding window rate limiter.
        
        Args:
            max_requests: Maximum requests in window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = defaultdict(list)
    
    def _clean_old_requests(self, key: str):
        """Remove requests outside the time window."""
        cutoff = datetime.utcnow() - timedelta(seconds=self.window_seconds)
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if req_time > cutoff
        ]
    
    async def check_rate_limit(self, request: Request, user_id: str):
        """Check if request is within rate limit."""
        key = f"{user_id}:{request.url.path}"
        
        # Clean old requests
        self._clean_old_requests(key)
        
        # Check limit
        if len(self.requests[key]) >= self.max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {self.max_requests} requests per {self.window_seconds} seconds.",
                headers={"Retry-After": str(self.window_seconds)}
            )
        
        # Add current request
        self.requests[key].append(datetime.utcnow())


# Global rate limiters
default_rate_limiter = RateLimiter(requests_per_minute=60, burst=10)
strict_rate_limiter = RateLimiter(requests_per_minute=20, burst=5)
sliding_window_limiter = SlidingWindowRateLimiter(max_requests=100, window_seconds=60)
