# 🛍️ Shopify Insights Fetcher

A Python-based application that fetches a Shopify store’s brand insights **without using the official Shopify API**, and structures them into an organized format. It also performs **BONUS competitor analysis** using Google search to extract similar insights from competitor Shopify stores.

---

## 📌 Features

✅ Fetch insights from any public Shopify store  
✅ Product catalog extraction  
✅ Hero products detection  
✅ Privacy & Return/Refund policy scraping  
✅ Brand FAQs (Q&A) extraction  
✅ Social media handles (Instagram, Facebook, TikTok, etc.)  
✅ Contact details (emails, phone numbers)  
✅ Brand context (About Us content)  
✅ Important links (Order Tracking, Blog, Contact Us, etc.)  
✅ Stores insights in a relational database  
✅ BONUS: Competitor analysis using Google search  
✅ Web UI with styled search input and popup error alerts  
✅ JSON API response with error handling  
✅ Pydantic + SQLAlchemy + FastAPI based backend

---

## 🧰 Tech Stack

- **Backend**: FastAPI, SQLAlchemy, Pydantic
- **Scraping**: BeautifulSoup, Requests
- **Database**: SQLite (default), PostgreSQL compatible
- **Frontend**: HTML + JavaScript (Jinja2 templates)
- **Others**: Python-dotenv, `googlesearch-python` for competitor detection

---

## 📂 Project Structure

