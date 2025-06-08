import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wantedlab.settings")
django.setup()

from django.core.wsgi import get_wsgi_application
from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware

from wantedlab.company.routers import router as company_router

app = FastAPI(title="Wanted Lab API")


django_app = WSGIMiddleware(get_wsgi_application())
app.mount("/django", django_app)


app.include_router(company_router, prefix="/api/v1", tags=["companies"])


@app.get("/")
async def root():
    return {"message": "Welcome to Wanted Lab"}
