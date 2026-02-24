# schemas.py
# These define the "shape" of data coming IN and going OUT

from pydantic import BaseModel, HttpUrl, field_validator
from datetime import datetime
from typing import Optional

# ============================================
# INPUT SCHEMAS (what client sends to us)
# ============================================

class URLCreate(BaseModel):
    # The URL to shorten
    # HttpUrl = Pydantic validates it's a real URL!
    # e.g., "google.com" would FAIL
    # e.g., "https://google.com" would PASS
    original_url: HttpUrl

    # Optional custom slug
    # str = string type
    # None = default value (not required)
    custom_slug: Optional[str] = None

    # Optional expiry in hours
    # int = integer type
    expires_in_hours: Optional[int] = None

    # Custom validator for slug
    # Runs automatically when slug is provided
    @field_validator('custom_slug')
    def validate_slug(cls, slug):
        if slug is None:
            return slug

        # Slug must be at least 3 characters
        if len(slug) < 3:
            raise ValueError('Slug must be at least 3 characters')

        # Slug must be max 10 characters
        if len(slug) > 10:
            raise ValueError('Slug must be max 10 characters')

        # Slug can only contain letters and numbers
        if not slug.isalnum():
            raise ValueError('Slug can only contain letters and numbers')

        # Convert to lowercase
        return slug.lower()


# ============================================
# OUTPUT SCHEMAS (what we send back to client)
# ============================================

class URLResponse(BaseModel):
    # These are the fields we return after shortening
    short_code: str
    short_url: str
    original_url: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    clicks: int

    # This tells Pydantic to read data from
    # SQLAlchemy objects (not just dictionaries)
    model_config = {"from_attributes": True}


class StatsResponse(BaseModel):
    short_code: str
    original_url: str
    total_clicks: int
    created_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool

    model_config = {"from_attributes": True}