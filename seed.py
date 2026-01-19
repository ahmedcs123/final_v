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
        {"name_en": "Chocolates", "name_ar": "الشوكولاتة", "slug": "chocolates"},
        {"name_en": "Coffee", "name_ar": "القهوة", "slug": "coffee"},
        {"name_en": "Flour", "name_ar": "الدقيق", "slug": "flour"},
        {"name_en": "Sweets", "name_ar": "الحلويات", "slug": "sweets"},
        {"name_en": "Frozen Meat", "name_ar": "اللحوم المجمدة", "slug": "frozen-meat"},
        {"name_en": "Frozen Chicken", "name_ar": "الدجاج المجمد", "slug": "frozen-chicken"},
        {"name_en": "Sugar", "name_ar": "السكر", "slug": "sugar"},
        {"name_en": "Raw Materials", "name_ar": "المواد الخام", "slug": "raw-materials"},
        {"name_en": "Creams & Fillings", "name_ar": "الكريمات والحشوات", "slug": "creams-fillings"},
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
            ),
            models.Product(
                category_id=cats.get("coffee"),
                name_en="Premium Arabica Coffee Beans",
                name_ar="حبوب قهوة أرابيكا فاخرة",
                code="COF-001",
                weight="1 KG",
                description_en="100% Arabica beans, medium roast.",
                description_ar="حبوب أرابيكا 100%، تحميص متوسط."
            ),
            models.Product(
                category_id=cats.get("flour"),
                name_en="All-Purpose Flour",
                name_ar="دقيق متعدد الاستخدامات",
                code="FLR-101",
                weight="50 KG",
                description_en="High quality flour for all baking needs.",
                description_ar="دقيق عالي الجودة لجميع احتياجات الخبز."
            ),
            models.Product(
                category_id=cats.get("sweets"),
                name_en="Assorted Gummies",
                name_ar="تشكيلة جيلي",
                code="SWT-005",
                weight="5 KG",
                description_en="Colorful fruit flavored gummy candies.",
                description_ar="حلوى جيلي بنكهات الفواكه الملونة."
            ),
            models.Product(
                category_id=cats.get("frozen-meat"),
                name_en="Premium Beef Tenderloin",
                name_ar="فيليه بقري فاخر",
                code="MT-012",
                weight="20 KG",
                description_en="High quality frozen beef tenderloin.",
                description_ar="فيليه بقري مجمد عالي الجودة."
            ),
            models.Product(
                category_id=cats.get("frozen-chicken"),
                name_en="Whole Frozen Chicken 1000g",
                name_ar="دجاج مجمد كامل 1000 جم",
                code="CHK-100",
                weight="10 KG Box",
                description_en="Grade A frozen whole chicken.",
                description_ar="دجاج كامل مجمد درجة أولى."
            ),
            models.Product(
                category_id=cats.get("sugar"),
                name_en="Fine White Sugar",
                name_ar="سكر أبيض ناعم",
                code="SUG-001",
                weight="50 KG",
                description_en="Refined white sugar for baking and sweetening.",
                description_ar="سكر أبيض مكرر للخبز والتحلية."
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
