import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from models import Product, FAQ, ContactDetails, SocialHandle, BrandContext
from typing import Optional
import json
import re

class ShopifyScraper:
    def __init__(self, website_url: str):
        # Initialize with the Shopify store's base URL
        self.website_url = website_url
        self.session = requests.Session()  # Use a session for connection reuse

    def fetch_page(self, path: str = "") -> Optional[BeautifulSoup]:
        """
        Fetches and parses an HTML page using BeautifulSoup.
        """
        try:
            response = self.session.get(urljoin(self.website_url, path), timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, "html.parser")
        except requests.RequestException:
            return None

    def get_product_catalog(self) -> list:
        """
        Retrieves the full product catalog from the Shopify `/products.json` endpoint.
        """
        try:
            response = self.session.get(urljoin(self.website_url, "/products.json"), timeout=10)
            response.raise_for_status()
            products = response.json().get("products", [])
            return [
                Product(
                    title=p["title"],
                    handle=p["handle"],
                    price=str(p.get("variants", [{}])[0].get("price", "")),
                    image=p.get("images", [{}])[0].get("src")
                )
                for p in products
            ]
        except requests.RequestException:
            return []

    def get_hero_products(self) -> list:
        """
        Scrapes prominent (hero/featured) products shown on the homepage.
        These are typically used in banners, carousels, or product cards.
        """
        soup = self.fetch_page()
        if not soup:
            return []

        products = []
        for item in soup.select(".product-card, .featured-product"):
            title = item.select_one(".product-title") or item.select_one("h3")
            title = title.text.strip() if title else ""

            handle = item.get("data-handle", "")
            
            price = item.select_one(".price") or item.select_one(".money")
            price = price.text.strip() if price else ""

            image = item.select_one("img")
            image = urljoin(self.website_url, image["src"]) if image and image.get("src") else ""

            if title and handle:
                products.append(Product(title=title, handle=handle, price=price, image=image))

        return products

    def get_policy(self, path: str) -> Optional[str]:
        """
        Fetches and extracts text from policy pages like privacy, refund, or return.
        """
        soup = self.fetch_page(path)
        if soup:
            content = soup.select_one(".page-content, .main-content")
            return content.text.strip() if content else None
        return None

    def get_faqs(self) -> list:
        """
        Extracts FAQ items from standard Shopify FAQ pages.
        """
        soup = self.fetch_page("/pages/faq") or self.fetch_page("/pages/faqs")
        if not soup:
            return []

        faqs = []
        for faq in soup.select(".faq-item, .accordion"):
            question = faq.select_one(".faq-question, .accordion-title")
            answer = faq.select_one(".faq-answer, .accordion-content")
            if question and answer:
                faqs.append(FAQ(question=question.text.strip(), answer=answer.text.strip()))
        return faqs

    def get_social_handles(self) -> list:
        """
        Detects social media links (Instagram, Facebook, TikTok) from the homepage.
        """
        soup = self.fetch_page()
        if not soup:
            return []

        socials = []
        for link in soup.select('a[href*="instagram.com"], a[href*="facebook.com"], a[href*="tiktok.com"]'):
            href = link["href"]
            platform = "Instagram" if "instagram" in href else "Facebook" if "facebook" in href else "TikTok"
            # Normalize URLs that may start with //
            absolute_url = urljoin("https:", href) if href.startswith("//") else urljoin(self.website_url, href)
            socials.append(SocialHandle(platform=platform, url=absolute_url))
        return socials

    def get_contact_details(self) -> ContactDetails:
        """
        Extracts contact details (emails, phone numbers, addresses) from the contact page.
        """
        soup = self.fetch_page("/pages/contact")
        emails, phones, addresses = [], [], []
        if soup:
            text = soup.get_text()
            # Regex to find emails and phone numbers
            emails = list(set(re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)))
            phones = list(set(re.findall(r"\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}", text)))
            # Attempt to extract addresses based on common classes
            address_tags = soup.select(".address, .contact-address")
            addresses = [tag.text.strip() for tag in address_tags]
        return ContactDetails(emails=emails, phones=phones, addresses=addresses)

    def get_brand_context(self) -> Optional[str]:
        """
        Fetches 'About Us' content for brand context/identity.
        """
        soup = self.fetch_page("/pages/about")
        if soup:
            content = soup.select_one(".about-content, .main-content")
            return content.text.strip() if content else None
        return None

    def get_important_links(self) -> dict:
        """
        Gathers links to essential pages like blog, contact, and order tracking.
        """
        soup = self.fetch_page()
        if not soup:
            return {}

        links = {}
        for link in soup.select('a[href*="/pages/"], a[href*="/track"], a[href*="/blogs"]'):
            text = link.text.strip().lower()
            if "track" in text:
                links["order_tracking"] = link["href"]
            elif "contact" in text:
                links["contact_us"] = link["href"]
            elif "blog" in text:
                links["blogs"] = link["href"]
        return {k: urljoin(self.website_url, v) for k, v in links.items()}

    def fetch_all(self) -> BrandContext:
        """
        Calls all sub-methods to collect and return a complete brand context.
        """
        return BrandContext(
            website_url=self.website_url,
            product_catalog=self.get_product_catalog(),
            hero_products=self.get_hero_products(),
            privacy_policy=self.get_policy("/pages/privacy-policy"),
            return_policy=self.get_policy("/pages/return-policy") or self.get_policy("/pages/refund-policy"),
            faqs=self.get_faqs(),
            social_handles=self.get_social_handles(),
            contact_details=self.get_contact_details(),
            brand_context=self.get_brand_context(),
            important_links=self.get_important_links()
        )
