from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_
from .. import database, models

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/")
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request, "active": "home"})

@router.get("/about")
def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request, "active": "about"})

@router.get("/contact")
def contact(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request, "active": "contact"})

@router.get("/products")
def products(request: Request, category_id: int = None, search: str = None, db: Session = Depends(database.get_db)):
    # Fetch categories for the filter sidebar
    categories = db.query(models.Category).all()
    
    # Start query
    query = db.query(models.Product)
    
    # Apply Filters
    if category_id:
        query = query.filter(models.Product.category_id == category_id)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                models.Product.name_en.ilike(search_term),
                models.Product.name_ar.ilike(search_term),
                models.Product.code.ilike(search_term)
            )
        )
    
    products_list = query.all()
    
    return templates.TemplateResponse("products.html", {
        "request": request, 
        "categories": categories, 
        "products": products_list,
        "selected_category": category_id,
        "search_term": search,
        "active": "products"
    })
