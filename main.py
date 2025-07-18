
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from services.ShopifyScraper import ShopifyScraper  # ✅ Correct if you're in app/
from services.competitor import CompetitorAnalyzer
from db.database import Database
from models import BrandRequest, BrandContext
from typing import Dict, List
import logging
from pydantic.json import pydantic_encoder
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize database and competitor service
db = Database()
competitor_analyzer = CompetitorAnalyzer()

@app.post("/fetch-insights", response_model=Dict[str, List[BrandContext]])
async def fetch_insights(request: BrandRequest):
    try:
        website_url = str(request.website_url).strip()
        logger.info(f"Fetching insights for URL: {website_url}")

        scraper = ShopifyScraper(website_url)
        brand_context = scraper.fetch_all()

        if not brand_context.product_catalog:
            raise HTTPException(status_code=404, detail="No products found or invalid store URL")
        
        #safe_brand_context = json.loads(json.dumps(brand_context.dict(), default=pydantic_encoder))
        safe_brand_context = json.loads(brand_context.json())
        db.save_insights(safe_brand_context, website_url)

        #db.save_insights(brand_context.dict(), website_url)

        brand_name = website_url.split(".")[0].replace("https://", "").replace("http://", "")
        competitor_insights = competitor_analyzer.fetch_competitor_insights(brand_name)

        return {
            "brand_insights": [brand_context],
            "competitor_insights": competitor_insights
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching insights: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")



@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
