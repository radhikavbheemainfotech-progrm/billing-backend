from fastapi import  FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes.auth import router as auth_router
from app.routes import  admin,product,category,dashboard

from app.database.db import Base,engine
import app.database.models
from app.routes import customer,order,business,upload
import os
from app.routes import customer


Base.metadata.create_all(bind=engine)


app  = FastAPI(
    title= "Billing Software API",
    description = "Direct billing and order management system",
   
)


os.makedirs("static/images",exist_ok=True)
app.mount("/static",StaticFiles(directory="static"),name = "static")
          
          
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
   allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return{"message":"Billing API is running"}




app.include_router(auth_router, prefix="/api/auth",tags=["Auth"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(product.router,prefix='/api/products',tags=["Products"])
app.include_router(customer.router,prefix="/api/customer",tags=["Customer"])
app.include_router(order.router,prefix="/api/orders", tags=["Orders"])
# app.include_router(invoice.router, prefix="/api/invoice", tags=["Invoice"])
app.include_router(category.router, prefix="/api/category", tags=["Category"])
app.include_router(dashboard.router, prefix="/api/admin/dashboard", tags=["Dashboard"])
# app.include_router(business.router, prefix="/api/business", tags=["Business"])
app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])