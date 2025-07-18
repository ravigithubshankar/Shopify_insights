from googlesearch import search
from services.ShopifyScraper import ShopifyScraper
from db.database import Database

class CompetitorAnalyzer:
    def __init__(self):
        self.db = Database()

    def find_competitors(self, brand_name: str, num_results: int = 3) -> list:
        competitors = []
        query = f"{brand_name} competitors site:*.myshopify.com"
        try:
            for url in search(query, num_results=num_results):
                if "myshopify.com" in url:
                    competitors.append(url)
        except Exception:
            pass
        return competitors

    def fetch_competitor_insights(self, brand_name: str) -> list:
        insights = []
        for url in self.find_competitors(brand_name):
            scraper = ShopifyScraper(url)
            brand_context = scraper.fetch_all()
            if brand_context.product_catalog:
                self.db.save_insights(brand_context.dict(), url)
                insights.append(brand_context)
        return insights
