from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
import os

#  DATABASE SETUP 
database_url = os.getenv('DATABASE_URL')

if database_url:
    
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    print("✅ Connected to Render PostgreSQL")
else:
    
    database_url = 'sqlite:///./inventory.db'
    print("⚠️  Using SQLite (local development)")

engine = create_engine(database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Model
class ProductModel(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50), default='General')
    quantity = Column(Integer, default=0)
    price = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'quantity': self.quantity,
            'price': self.price,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# Create tables
Base.metadata.create_all(bind=engine)

#  PYDANTIC SCHEMAS 
class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    category: str = Field(default='General', max_length=50)
    quantity: int = Field(default=0, ge=0)
    price: float = Field(default=0.0, ge=0)

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    category: Optional[str] = Field(None, max_length=50)
    quantity: Optional[int] = Field(None, ge=0)
    price: Optional[float] = Field(None, ge=0)

class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

class StatsResponse(BaseModel):
    total_products: int
    total_quantity: int
    total_inventory_value: float
    database_type: str

class HealthResponse(BaseModel):
    status: str
    database: str
    timestamp: datetime

# FASTAPI APP
app = FastAPI(
    title="Inventory API",
    description="FastAPI version of the Inventory Management System",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#  API ROUTES 
@app.get("/", response_model=dict)
async def home():
    return {
        "message": "🚀 Inventory API Deployed on Render! (FastAPI Version)",
        "database": "PostgreSQL" if 'postgresql' in database_url else "SQLite",
        "status": "running",
        "endpoints": [
            "GET /api/products - Get all products",
            "POST /api/products - Add new product",
            "GET /api/products/{id} - Get single product",
            "PUT /api/products/{id} - Update product",
            "DELETE /api/products/{id} - Delete product",
            "GET /api/stats - Get inventory statistics",
            "GET /api/health - Check API health"
        ]
    }

@app.get("/api/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="healthy",
        database="postgresql" if 'postgresql' in database_url else "sqlite",
        timestamp=datetime.utcnow()
    )

@app.get("/api/products", response_model=List[ProductResponse])
async def get_products(db: Session = Depends(get_db)):
    products = db.query(ProductModel).order_by(ProductModel.created_at.desc()).all()
    return products

@app.post("/api/products", response_model=ProductResponse, status_code=201)
async def add_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = ProductModel(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.get("/api/products/{id}", response_model=ProductResponse)
async def get_product(id: int, db: Session = Depends(get_db)):
    product = db.query(ProductModel).filter(ProductModel.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.put("/api/products/{id}", response_model=ProductResponse)
async def update_product(id: int, product_update: ProductUpdate, db: Session = Depends(get_db)):
    db_product = db.query(ProductModel).filter(ProductModel.id == id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    update_data = product_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_product, field, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product

@app.delete("/api/products/{id}")
async def delete_product(id: int, db: Session = Depends(get_db)):
    product = db.query(ProductModel).filter(ProductModel.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(product)
    db.commit()
    return {"message": "Product deleted"}

@app.get("/api/stats", response_model=StatsResponse)
async def stats(db: Session = Depends(get_db)):
    total_products = db.query(func.count(ProductModel.id)).scalar()
    total_quantity = db.query(func.sum(ProductModel.quantity)).scalar() or 0
    total_value = db.query(func.sum(ProductModel.price * ProductModel.quantity)).scalar() or 0
    
    return StatsResponse(
        total_products=total_products,
        total_quantity=total_quantity,
        total_inventory_value=float(total_value),
        database_type="PostgreSQL" if 'postgresql' in database_url else "SQLite"
    )

#  MAIN ENTRY POINT 
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv('PORT', 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
