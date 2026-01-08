from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CategoryBase(BaseModel):
    name_en: str
    name_ar: str
    slug: str
    image: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    category_id: int
    name_en: str
    name_ar: str
    code: str
    weight: str
    description_en: Optional[str] = None
    description_ar: Optional[str] = None
    image: Optional[str] = "placeholder.jpg"

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ProductWithCategory(Product):
    category: Category

class AdminBase(BaseModel):
    username: str

class AdminCreate(AdminBase):
    password: str
    role: Optional[str] = "admin"

class Admin(AdminBase):
    id: int
    role: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None
