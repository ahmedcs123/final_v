from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models

def seed_data():
    db = SessionLocal()
    
    print("Checking for existing data...")
    # Optional: Clear existing data to force update (Be careful in prod, okay for dev/seed)
    # db.query(models.Product).delete()
    # db.query(models.Category).delete()
    # db.commit()

    # Define Categories
    categories_data = [
        {"name_en": "Raw Materials", "name_ar": "المواد الخام", "slug": "raw-materials"},
        {"name_en": "Chocolates", "name_ar": "الشوكولاتة", "slug": "chocolates"},
        {"name_en": "Creams & Fillings", "name_ar": "الكريمات والحشوات", "slug": "creams-fillings"},
        {"name_en": "Cake Decoration", "name_ar": "زينة الكيك", "slug": "cake-decoration"},
        {"name_en": "Ice Cream & Gelato", "name_ar": "الآيس كريم والجيلاتو", "slug": "ice-cream-gelato"},
        {"name_en": "Beverages", "name_ar": "المشروبات", "slug": "beverages"},
    ]

    for cat_data in categories_data:
        existing = db.query(models.Category).filter_by(slug=cat_data["slug"]).first()
        if not existing:
            print(f"Adding category: {cat_data['name_en']}")
            new_cat = models.Category(
                name_en=cat_data["name_en"],
                name_ar=cat_data["name_ar"],
                slug=cat_data["slug"]
            )
            db.add(new_cat)
        else:
             print(f"Category exists: {cat_data['name_en']}")
    
    db.commit()

    # Add some sample products for the new categories if none exist
    # Fetch categories again to get IDs
    cats = {c.slug: c.id for c in db.query(models.Category).all()}
    
    if db.query(models.Product).count() == 0:
        print("Seeding sample products...")
        products = [
            models.Product(
                category_id=cats.get("chocolates"),
                name_en="Dark Chocolate Couverture 70%",
                name_ar="شوكولاتة خام داكنة 70%",
                code="CHOC-001",
                weight="10 KG",
                description_en="Premium dark chocolate drops for baking and molding.",
                description_ar="رقائق شوكولاتة داكنة فاخرة للخبز والتشكيل."
            ),
            models.Product(
                category_id=cats.get("raw-materials"),
                name_en="Almond Flour",
                name_ar="دقيق اللوز",
                code="RAW-005",
                weight="5 KG",
                description_en="Finely ground blanched almond flour.",
                description_ar="دقيق لوز مقشر ومطحون ناعم."
            ),
            models.Product(
                 category_id=cats.get("ice-cream-gelato"),
                name_en="Vanilla Gelato Base",
                name_ar="قاعدة جيلاتو فانيليا",
                code="ICE-020",
                weight="2 KG",
                description_en="High quality base for vanilla gelato.",
                description_ar="قاعدة عالية الجودة لجيلاتو الفانيليا."
            )
        ]
        for p in products:
            if p.category_id: # Only add if category was found
                db.add(p)
        db.commit()
    
    print("Seeding complete.")
    db.close()

if __name__ == "__main__":
    seed_data()
