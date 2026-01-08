from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app import models, database, auth
from app.routers import public, admin

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="The Vines Trading Company")

@app.on_event("startup")
def on_startup():
    db = database.SessionLocal()
    try:
        auth.create_super_admin_if_not_exists(db)
    finally:
        db.close()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

app.include_router(public.router)
app.include_router(admin.router)
