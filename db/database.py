from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, BrandInsight
from typing import Optional
import os
from dotenv import load_dotenv
from pydantic import HttpUrl

# Load environment variables from .env file
load_dotenv()

def convert_httpurl_to_str(data):
    """
    Recursively converts all HttpUrl fields (or other nested non-primitive fields)
    to plain strings so they can be stored in a database.
    """
    if isinstance(data, dict):
        return {k: convert_httpurl_to_str(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_httpurl_to_str(item) for item in data]
    elif isinstance(data, HttpUrl):
        return str(data)
    return data

class Database:
    def __init__(self):
        """
        Initialize the database connection using the DATABASE_URL from environment.
        Creates the required tables using SQLAlchemy's ORM model.
        """
        self.engine = create_engine(os.getenv("DATABASE_URL"))
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def save_insights(self, brand_context: dict, website_url: str) -> None:
        """
        Saves or updates brand insights into the database for a given Shopify website URL.

        Parameters:
        - brand_context (dict): Dictionary of insights extracted by the scraper.
        - website_url (str): The Shopify store URL associated with the insights.
        """
        session = self.Session()
        try:
            # Convert all Pydantic/complex fields (e.g., HttpUrl) into serializable primitives
            brand_context = convert_httpurl_to_str(brand_context)

            # Check if entry for the website already exists in DB
            existing = session.query(BrandInsight).filter_by(website_url=website_url).first()

            if existing:
                # Update existing record with new data
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
                # Create new entry if not already in DB
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

            # Persist changes to the DB
            session.commit()
        except Exception as e:
            # Roll back in case of failure
            session.rollback()
            raise e
        finally:
            # Always close the session
            session.close()
