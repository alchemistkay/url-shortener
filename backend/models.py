# ============================================
# IMPORTS - Tools we need
# ============================================

# Column = defines a table column
# Integer, String, etc. = data types
# DateTime = stores dates and times
# Boolean = True/False values
# ForeignKey = links tables together
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey

# func = SQL functions (like getting current time)
from sqlalchemy.sql import func

# relationship = defines how tables relate to each other
from sqlalchemy.orm import relationship

# Base = parent class we defined in database.py
from database import Base


# ============================================
# URL MODEL
# ============================================

class URL(Base):
    # __tablename__ tells SQLAlchemy what to call
    # this table in the database
    __tablename__ = "urls"

    # PRIMARY KEY - unique ID for each row
    # Integer = whole numbers (1, 2, 3...)
    # primary_key=True = this is unique identifier
    # index=True = makes lookups faster
    id = Column(Integer, primary_key=True, index=True)

    # The original long URL
    # String = text data
    # nullable=False = REQUIRED (can't be empty)
    original_url = Column(String, nullable=False)

    # The short code (e.g., "abc123")
    # unique=True = no two URLs can have same code
    # index=True = fast lookups (we search by this!)
    short_code = Column(String(10), unique=True, index=True, nullable=False)

    # Was a custom slug chosen by user?
    # Boolean = True or False
    # default=False = unless specified, it's False
    is_custom = Column(Boolean, default=False)

    # When was this URL created?
    # server_default=func.now() = database sets
    # this automatically when row is created
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # When does this URL expire? (optional)
    # nullable=True = this CAN be empty (no expiry)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    # How many times has this been clicked?
    # default=0 = starts at zero
    clicks = Column(Integer, default=0)

    # Is this URL still working?
    # Allows us to disable without deleting
    is_active = Column(Boolean, default=True)

    # RELATIONSHIP - connects URL to its clicks
    # "Click" = the other model (defined below)
    # back_populates = the matching relationship name
    # cascade = if URL deleted, delete its clicks too
    click_records = relationship(
        "Click",
        back_populates="url",
        cascade="all, delete-orphan"
    )

    # __repr__ = how Python displays this object
    # Useful for debugging
    def __repr__(self):
        return f"<URL {self.short_code} → {self.original_url}>"


# ============================================
# CLICK MODEL
# ============================================

class Click(Base):
    __tablename__ = "clicks"

    id = Column(Integer, primary_key=True, index=True)

    # FOREIGN KEY - links to URLs table
    # "urls.id" = references the id column in urls table
    # This is how we know WHICH URL was clicked
    url_id = Column(Integer, ForeignKey("urls.id"), nullable=False, index=True)

    # When was the click recorded?
    clicked_at = Column(DateTime(timezone=True), server_default=func.now())

    # What browser/device made the request?
    # nullable=True = optional information
    user_agent = Column(String, nullable=True)

    # Where did the visitor come from?
    # e.g., "https://twitter.com"
    referer = Column(String, nullable=True)

    # RELATIONSHIP - connects click back to its URL
    # back_populates must match the URL model relationship name
    url = relationship("URL", back_populates="click_records")

    def __repr__(self):
        return f"<Click on URL {self.url_id} at {self.clicked_at}>"