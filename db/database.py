from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, BrandInsight
from typing import Optional
import os
from dotenv import load_dotenv
from pydantic import HttpUrl

load_dotenv()

def convert_httpurl_to_str(data):
    """Recursively converts all HttpUrl values to str in nested dicts/lists"""
    if isinstance(data, dict):
        return {k: convert_httpurl_to_str(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_httpurl_to_str(item) for item in data]
    elif isinstance(data, HttpUrl):
        return str(data)
    return data

class Database:
    def __init__(self):
        self.engine = create_engine(os.getenv("DATABASE_URL"))
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def save_insights(self, brand_context: dict, website_url: str) -> None:
        session = self.Session()
        try:
            # Convert all HttpUrl and other non-serializable fields to primitive types
            brand_context = convert_httpurl_to_str(brand_context)

            existing = session.query(BrandInsight).filter_by(website_url=website_url).first()

            if existing:
                existing.product_catalog = brand_context["product_catalog"]
                existing.hero_products = brand_context["hero_products"]
                existing.privacy_policy = brand_context["privacy_policy"]
                existing.return_policy = brand_context["return_policy"]
                existing.faqs = brand_context["faqs"]
                existing.social_handles = brand_context["social_handles"]
                existing.contact_details = brand_context["contact_details"]
                existing.brand_context = brand_context["brand_context"]
                existing.important_links = brand_context["important_links"]
            else:
                insight = BrandInsight(
                    website_url=website_url,
                    product_catalog=brand_context["product_catalog"],
                    hero_products=brand_context["hero_products"],
                    privacy_policy=brand_context["privacy_policy"],
                    return_policy=brand_context["return_policy"],
                    faqs=brand_context["faqs"],
                    social_handles=brand_context["social_handles"],
                    contact_details=brand_context["contact_details"],
                    brand_context=brand_context["brand_context"],
                    important_links=brand_context["important_links"]
                )
                session.add(insight)

            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
