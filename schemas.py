"""
Database Schemas for Arcadia

Pydantic models map to MongoDB collections (lowercased class names).
"""
from typing import Optional, List, Literal
from pydantic import BaseModel, Field


class Product(BaseModel):
    slug: str = Field(..., description="URL-friendly unique identifier")
    name: str
    subtitle: Optional[str] = None
    description: Optional[str] = None
    base_price: float = Field(..., ge=0)
    models: List[str] = Field(default_factory=lambda: ["Halo", "Prism", "Crescent"])  # stylistic families
    finishes: List[Literal["gold", "black", "silver"]] = ["gold", "black", "silver"]
    sizes: List[Literal["S", "M", "L", "XL"]] = ["S", "M", "L", "XL"]
    temperatures: List[int] = [3000, 4000, 5000, 6500]
    hero_image: Optional[str] = None
    gallery: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)


class Review(BaseModel):
    product_slug: str
    author: str
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


class BlogPost(BaseModel):
    slug: str
    title: str
    excerpt: Optional[str] = None
    content: str
    cover_image: Optional[str] = None


class FAQ(BaseModel):
    question: str
    answer: str
