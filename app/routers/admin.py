from fastapi import APIRouter, Request, Depends, Form, File, UploadFile, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .. import database, models, auth
import shutil
import os

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("admin/login.html", {"request": request})

@router.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(database.get_db)):
    user = auth.authenticate_user(db, username, password)
    if not user:
         return templates.TemplateResponse("admin/login.html", {"request": request, "error": "Invalid credentials"})
    
    access_token = auth.create_access_token(data={"sub": user.username})
    response = RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response

@router.get("/logout")
def logout():
    response = RedirectResponse(url="/admin/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="access_token")
    return response

@router.get("/dashboard")
def dashboard(request: Request, user: models.Admin = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    if not user:
        return RedirectResponse(url="/admin/login")
    
    products = db.query(models.Product).all()
    categories = db.query(models.Category).all()
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request, 
        "user": user, 
        "products": products,
        "categories": categories
    })

# --- Super Admin: User Management ---
@router.get("/users")
def manage_users(request: Request, user: models.Admin = Depends(auth.get_current_active_superuser), db: Session = Depends(database.get_db)):
    admins = db.query(models.Admin).all()
    return templates.TemplateResponse("admin/users.html", {
        "request": request,
        "user": user,
        "admins": admins
    })

@router.post("/users/add")
def add_admin(
    username: str = Form(...), password: str = Form(...), role: str = Form(...),
    current_user: models.Admin = Depends(auth.get_current_active_superuser),
    db: Session = Depends(database.get_db)
):
    # Check if username exists
    if db.query(models.Admin).filter(models.Admin.username == username).first():
        # Ideally return error, simplified for now
        return RedirectResponse(url="/admin/users?error=UsernameExists", status_code=status.HTTP_303_SEE_OTHER)
    
    password_hash = auth.get_password_hash(password)
    new_admin = models.Admin(username=username, password_hash=password_hash, role=role)
    db.add(new_admin)
    db.commit()
    return RedirectResponse(url="/admin/users", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/users/delete/{admin_id}")
def delete_admin(
    admin_id: int,
    current_user: models.Admin = Depends(auth.get_current_active_superuser),
    db: Session = Depends(database.get_db)
):
    admin_to_delete = db.query(models.Admin).filter(models.Admin.id == admin_id).first()
    if admin_to_delete and admin_to_delete.id != current_user.id: # Prevent self-delete
        db.delete(admin_to_delete)
        db.commit()
    return RedirectResponse(url="/admin/users", status_code=status.HTTP_303_SEE_OTHER)

# --- Product CRUD ---
@router.post("/products/add")
async def add_product(
    request: Request,
    name_en: str = Form(...), name_ar: str = Form(...),
    code: str = Form(...), weight: str = Form(...),
    category_id: int = Form(...),
    description_en: str = Form(""), description_ar: str = Form(""),
    image: UploadFile = File(None),
    user: models.Admin = Depends(auth.login_required),
    db: Session = Depends(database.get_db)
):
    image_path = None
    if image and image.filename:
        # Save image
        upload_dir = "app/static/uploads"
        os.makedirs(upload_dir, exist_ok=True)
        filename = f"{code}_{image.filename}" # Unique-ify
        file_location = f"{upload_dir}/{filename}"
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(image.file, file_object)
        image_path = f"/static/uploads/{filename}"

    new_product = models.Product(
        name_en=name_en, name_ar=name_ar,
        code=code, weight=weight,
        category_id=category_id,
        description_en=description_en, description_ar=description_ar,
        image=image_path
    )
    try:
        db.add(new_product)
        db.commit()
    except Exception:
        db.rollback()
        # Handle unique logic error if needed
        pass
        
    return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/products/delete/{product_id}")
def delete_product(product_id: int, user: models.Admin = Depends(auth.login_required), db: Session = Depends(database.get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if product:
        db.delete(product)
        db.commit()
    return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/products/edit/{product_id}")
async def edit_product(
    product_id: int,
    request: Request,
    name_en: str = Form(...), name_ar: str = Form(...),
    code: str = Form(...), weight: str = Form(...),
    category_id: int = Form(...),
    description_en: str = Form(""), description_ar: str = Form(""),
    image: UploadFile = File(None),
    user: models.Admin = Depends(auth.login_required),
    db: Session = Depends(database.get_db)
):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        return RedirectResponse(url="/admin/dashboard?error=ProductNotFound", status_code=status.HTTP_303_SEE_OTHER)
    
    # Update fields
    product.name_en = name_en
    product.name_ar = name_ar
    product.code = code
    product.weight = weight
    product.category_id = category_id
    product.description_en = description_en
    product.description_ar = description_ar

    if image and image.filename:
        # Save new image
        upload_dir = "app/static/uploads"
        os.makedirs(upload_dir, exist_ok=True)
        filename = f"{code}_{image.filename}"
        file_location = f"{upload_dir}/{filename}"
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(image.file, file_object)
        product.image = f"/static/uploads/{filename}"

    try:
        db.commit()
    except Exception:
        db.rollback()
    
    return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_303_SEE_OTHER)


# --- Category CRUD ---
@router.post("/categories/add")
async def add_category(
    name_en: str = Form(...), name_ar: str = Form(...),
    slug: str = Form(...),
    user: models.Admin = Depends(auth.login_required),
    db: Session = Depends(database.get_db)
):
    new_cat = models.Category(
        name_en=name_en, name_ar=name_ar,
        slug=slug
    )
    try:
        db.add(new_cat)
        db.commit()
    except Exception:
        db.rollback()
    return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/categories/delete/{category_id}")
def delete_category(category_id: int, user: models.Admin = Depends(auth.login_required), db: Session = Depends(database.get_db)):
    cat = db.query(models.Category).filter(models.Category.id == category_id).first()
    if cat:
        db.delete(cat)
        db.commit()
    return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/categories/edit/{category_id}")
async def edit_category(
    category_id: int,
    name_en: str = Form(...), name_ar: str = Form(...),
    slug: str = Form(...),
    user: models.Admin = Depends(auth.login_required),
    db: Session = Depends(database.get_db)
):
    cat = db.query(models.Category).filter(models.Category.id == category_id).first()
    if cat:
        cat.name_en = name_en
        cat.name_ar = name_ar
        cat.slug = slug
        try:
            db.commit()
        except:
            db.rollback()
            
    return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/products/edit/{product_id}")
async def edit_product(
    product_id: int,
    request: Request,
    name_en: str = Form(...), name_ar: str = Form(...),
    code: str = Form(...), weight: str = Form(...),
    category_id: int = Form(...),
    description_en: str = Form(""), description_ar: str = Form(""),
    image: UploadFile = File(None),
    user: models.Admin = Depends(auth.login_required),
    db: Session = Depends(database.get_db)
):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        return RedirectResponse(url="/admin/dashboard?error=ProductNotFound", status_code=status.HTTP_303_SEE_OTHER)
    
    # Update fields
    product.name_en = name_en
    product.name_ar = name_ar
    product.code = code
    product.weight = weight
    product.category_id = category_id
    product.description_en = description_en
    product.description_ar = description_ar

    if image and image.filename:
        # Save new image
        upload_dir = "app/static/uploads"
        os.makedirs(upload_dir, exist_ok=True)
        filename = f"{code}_{image.filename}"
        file_location = f"{upload_dir}/{filename}"
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(image.file, file_object)
        product.image = f"/static/uploads/{filename}"

    try:
        db.commit()
    except Exception:
        db.rollback()
    
    return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_303_SEE_OTHER)


# --- Category CRUD ---
@router.post("/categories/add")
async def add_category(
    name_en: str = Form(...), name_ar: str = Form(...),
    slug: str = Form(...),
    user: models.Admin = Depends(auth.login_required),
    db: Session = Depends(database.get_db)
):
    new_cat = models.Category(
        name_en=name_en, name_ar=name_ar,
        slug=slug
    )
    try:
        db.add(new_cat)
        db.commit()
    except Exception:
        db.rollback()
    return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/categories/delete/{category_id}")
def delete_category(category_id: int, user: models.Admin = Depends(auth.login_required), db: Session = Depends(database.get_db)):
    cat = db.query(models.Category).filter(models.Category.id == category_id).first()
    if cat:
        db.delete(cat)
        db.commit()
    return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/categories/edit/{category_id}")
async def edit_category(
    category_id: int,
    name_en: str = Form(...), name_ar: str = Form(...),
    slug: str = Form(...),
    user: models.Admin = Depends(auth.login_required),
    db: Session = Depends(database.get_db)
):
    cat = db.query(models.Category).filter(models.Category.id == category_id).first()
    if cat:
        cat.name_en = name_en
        cat.name_ar = name_ar
        cat.slug = slug
        try:
            db.commit()
        except:
            db.rollback()
            
    return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_303_SEE_OTHER)
