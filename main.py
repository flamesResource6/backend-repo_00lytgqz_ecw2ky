import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents
from schemas import Product as ProductSchema, Review as ReviewSchema, BlogPost as BlogPostSchema, FAQ as FAQSchema

app = FastAPI(title="Arcadia API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Utility ----------
COLL_PRODUCT = "product"
COLL_REVIEW = "review"
COLL_BLOGPOST = "blogpost"
COLL_FAQ = "faq"


def bootstrap_if_empty():
    if db is None:
        return
    try:
        # Seed products
        if db[COLL_PRODUCT].count_documents({}) == 0:
            samples: List[dict] = [
                {
                    "slug": "arcadia-halo",
                    "name": "Arcadia Halo",
                    "subtitle": "Circular luminous sculpture",
                    "description": "A levitating ring of light with precision-milled frame and crystal diffusion.",
                    "base_price": 1890.0,
                    "models": ["Halo"],
                    "finishes": ["gold", "black", "silver"],
                    "sizes": ["S", "M", "L", "XL"],
                    "temperatures": [3000, 4000, 5000, 6500],
                    "hero_image": "https://images.unsplash.com/photo-1504196606672-aef5c9cefc92?q=80&w=1600&auto=format&fit=crop",
                    "gallery": [
                        "https://images.unsplash.com/photo-1519710164239-da123dc03ef4?q=80&w=1600&auto=format&fit=crop",
                        "https://images.unsplash.com/photo-1524758631624-e2822e304c36?q=80&w=1600&auto=format&fit=crop"
                    ],
                    "tags": ["halo", "ring", "modern"]
                },
                {
                    "slug": "arcadia-prism",
                    "name": "Arcadia Prism",
                    "subtitle": "Faceted architectural statement",
                    "description": "Multi-faceted body that refracts light like a crystal with smart dimming.",
                    "base_price": 2390.0,
                    "models": ["Prism"],
                    "finishes": ["gold", "black", "silver"],
                    "sizes": ["S", "M", "L"],
                    "temperatures": [3000, 4000, 5000, 6500],
                    "hero_image": "https://images.unsplash.com/photo-1501785888041-af3ef285b470?q=80&w=1600&auto=format&fit=crop",
                    "gallery": [],
                    "tags": ["prism", "crystal", "futuristic"]
                },
                {
                    "slug": "arcadia-crescent",
                    "name": "Arcadia Crescent",
                    "subtitle": "Sculptural curve with diffused glow",
                    "description": "Soft curvature meets aerospace aluminum with satin finishes.",
                    "base_price": 2090.0,
                    "models": ["Crescent"],
                    "finishes": ["gold", "black", "silver"],
                    "sizes": ["M", "L", "XL"],
                    "temperatures": [3000, 4000, 5000],
                    "hero_image": "https://images.unsplash.com/photo-1505691723518-36a5ac3b2d91?q=80&w=1600&auto=format&fit=crop",
                    "gallery": [],
                    "tags": ["crescent", "curve", "elegant"]
                }
            ]
            for s in samples:
                create_document(COLL_PRODUCT, s)
        # Seed FAQs
        if db[COLL_FAQ].count_documents({}) == 0:
            faqs = [
                {"question": "How do I install Arcadia chandeliers?", "answer": "Each product includes a precision mount, balance guide, and video tutorial."},
                {"question": "What is the lifespan?", "answer": "High-efficiency LEDs rated for 50,000 hours with replaceable drivers."},
                {"question": "Smart control?", "answer": "Works with Arcadia app, HomeKit, Alexa, and Google Home."}
            ]
            for f in faqs:
                create_document(COLL_FAQ, f)
        # Seed blog
        if db[COLL_BLOGPOST].count_documents({}) == 0:
            posts = [
                {"slug": "light-as-architecture", "title": "Light as Architecture", "excerpt": "How luminous forms shape space.", "content": "In Arcadia, light is a structural medium...", "cover_image": "https://images.unsplash.com/photo-1496307653780-42ee777d4833?q=80&w=1600&auto=format&fit=crop"},
                {"slug": "future-of-luminaires", "title": "The Future of Luminaires", "excerpt": "Materials, intelligence, sustainability.", "content": "From aerospace alloys to neural dimming...", "cover_image": "https://images.unsplash.com/photo-1482192596544-9eb780fc7f66?q=80&w=1600&auto=format&fit=crop"}
            ]
            for p in posts:
                create_document(COLL_BLOGPOST, p)
    except Exception:
        # If seeding fails, continue without blocking
        pass


bootstrap_if_empty()


# ---------- Models for requests ----------
class PriceRequest(BaseModel):
    slug: str
    finish: str
    size: str
    temperature: int


# ---------- Routes ----------
@app.get("/")
def read_root():
    return {"brand": "Arcadia", "status": "ok"}


@app.get("/api/products")
def list_products():
    products = get_documents(COLL_PRODUCT)
    return products


@app.get("/api/products/{slug}")
def get_product(slug: str):
    product = db[COLL_PRODUCT].find_one({"slug": slug}) if db else None
    if not product:
        raise HTTPException(404, "Product not found")
    # Convert ObjectId
    product["_id"] = str(product["_id"]) if "_id" in product else None
    return product


@app.get("/api/reviews")
def list_reviews(product: Optional[str] = Query(None, alias="product")):
    filt = {"product_slug": product} if product else {}
    reviews = get_documents(COLL_REVIEW, filt)
    for r in reviews:
        if "_id" in r:
            r["_id"] = str(r["_id"])
    return reviews


@app.post("/api/reviews")
def add_review(review: ReviewSchema):
    _id = create_document(COLL_REVIEW, review)
    return {"inserted_id": _id}


@app.get("/api/blog")
def list_blog():
    posts = get_documents(COLL_BLOGPOST)
    for p in posts:
        if "_id" in p:
            p["_id"] = str(p["_id"])
    return posts


@app.get("/api/blog/{slug}")
def get_blog(slug: str):
    doc = db[COLL_BLOGPOST].find_one({"slug": slug}) if db else None
    if not doc:
        raise HTTPException(404, "Post not found")
    doc["_id"] = str(doc["_id"]) if "_id" in doc else None
    return doc


@app.get("/api/faq")
def list_faq():
    faqs = get_documents(COLL_FAQ)
    for f in faqs:
        if "_id" in f:
            f["_id"] = str(f["_id"])
    return faqs


@app.post("/api/price")
def calculate_price(req: PriceRequest):
    # Pricing: base + finish adj + size adj + temperature adj
    prod = db[COLL_PRODUCT].find_one({"slug": req.slug}) if db else None
    if not prod:
        raise HTTPException(404, "Product not found")
    price = float(prod.get("base_price", 1000))
    finish_factor = {"gold": 1.15, "black": 1.0, "silver": 1.08}.get(req.finish, 1.0)
    size_factor = {"S": 0.9, "M": 1.0, "L": 1.2, "XL": 1.45}.get(req.size, 1.0)
    temp_factor = 1.0 if req.temperature in [3000, 4000] else 1.05
    total = round(price * finish_factor * size_factor * temp_factor, 2)
    return {"price": total}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
