from pydantic import BaseModel, HttpUrl, EmailStr
from typing import List, Optional, Dict
from sqlalchemy import Column, Integer, String, Text, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# SQLAlchemy Models for Database
class BrandInsight(Base):
    __tablename__ = "brand_insights"
    id = Column(Integer, primary_key=True, index=True)
    website_url = Column(String(255), unique=True, index=True)
    product_catalog = Column(JSON)
    hero_products = Column(JSON)
    privacy_policy = Column(Text)
    return_policy = Column(Text)
    faqs = Column(JSON)
    social_handles = Column(JSON)
    contact_details = Column(JSON)
    brand_context = Column(Text)
    important_links = Column(JSON)

# Pydantic Models for API
class Product(BaseModel):
    title: str
    handle: str
    price: Optional[str]
    image: Optional[HttpUrl]

class FAQ(BaseModel):
    question: str
    answer: str

class ContactDetails(BaseModel):
    emails: List[EmailStr] = []
    phones: List[str] = []
    addresses: List[str] = []

class SocialHandle(BaseModel):
    platform: str
    url: HttpUrl

class BrandContext(BaseModel):
    website_url: HttpUrl
    product_catalog: List[Product]
    hero_products: List[Product]
    privacy_policy: Optional[str]
    return_policy: Optional[str]
    faqs: List[FAQ]
    social_handles: List[SocialHandle]
    contact_details: ContactDetails
    brand_context: Optional[str]
    important_links: Dict[str, HttpUrl]

class BrandRequest(BaseModel):
    website_url: HttpUrl