from googlesearch import search
from services.ShopifyScraper import ShopifyScraper
from db.database import Database

class CompetitorAnalyzer:
    def __init__(self):
        # Initialize the database connection to store competitor insights
        self.db = Database()

    def find_competitors(self, brand_name: str, num_results: int = 3) -> list:
        """
        Uses Google search to find competitor Shopify store URLs based on a brand name.
        Example query: "nike competitors site:*.myshopify.com"
        """
        competitors = []
        query = f"{brand_name} competitors site:*.myshopify.com"
        try:
            # Perform Google search and collect relevant Shopify URLs
            for url in search(query, num_results=num_results):
                if "myshopify.com" in url:
                    competitors.append(url)
        except Exception:
            # Fail silently if search fails (e.g., due to network or API limits)
            pass
        return competitors

    def fetch_competitor_insights(self, brand_name: str) -> list:
        """
        Fetches insights (product catalog, metadata, etc.) from competitor Shopify stores.
        Scrapes each competitor URL and stores the data in the database.
        """
        insights = []
        for url in self.find_competitors(brand_name):
            # Initialize scraper with the competitor URL
            scraper = ShopifyScraper(url)
            
            # Extract data from the competitor store
            brand_context = scraper.fetch_all()
            
            # Save to DB only if valid product catalog is found
            if brand_context.product_catalog:
                self.db.save_insights(brand_context.dict(), url)
                insights.append(brand_context)
                
        return insights
