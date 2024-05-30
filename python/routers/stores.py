from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from typing import List, Optional
from typing import AsyncGenerator
from sqlalchemy import Column, Integer, String, Text, Double, Float, join
from pydantic import BaseModel
from typing import List
from sqlalchemy.sql.expression import func
from sqlalchemy import text



DATABASE_URL = "postgresql+asyncpg://postgres:ProLab895+@localhost:5432/pizza"

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

class Store(Base):
    __tablename__ = "stores"
    storeid = Column(Text, primary_key=True, index=True)
    zipcode = Column(Integer)
    state_abbr = Column(Text)
    latitude = Column(Float)
    longitude = Column(Float)
    city = Column(Text)
    state = Column(Text)
    distance = Column(Float)

class StoreModel(BaseModel):
    storeid: str
    zipcode: int
    state_abbr: str
    latitude: float
    longitude: float
    city: str
    state: str
    distance: float

    class Config:
        orm_mode = True
        from_attributes = True
        
    class ProductSales(Base):
        __tablename__ = "product_sales"
        SKU = Column(String, primary_key=True)
        name = Column(String)
        size = Column(String)
        TotalSold = Column(Integer)
    
    class OrderItems(Base):
        __tablename__ = "order_items"
        sku = Column(String, primary_key=True)
        orderid = Column(Integer)
    # Weitere Spalten nach Bedarf
    

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

router = APIRouter()

@router.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@router.get('/stores/', response_model=List[StoreModel])
async def read_stores(filter: Optional[str] = Query(None, title="Filter", description="Filter for stores"), session: AsyncSession = Depends(get_session)):
    query = select(Store)
    if filter:
        query = query.where(Store.state_abbr.like(f"%{filter}%")) 
    result = await session.execute(query)
    stores = result.scalars().all()
    return [StoreModel.from_orm(store) for store in stores]

@router.get("/top-selling-products")
async def get_top_selling_products(session: AsyncSession = Depends(get_session)):
    query = text("""
        SELECT products.name, products.size, COUNT(order_items.sku) AS TotalSold
        FROM public.products
        INNER JOIN public.order_items ON products.sku = order_items.sku
        INNER JOIN public.orders ON order_items.orderid = orders.orderid
        GROUP BY products.name, products.size;
    """)
    result = await session.execute(query)
    products = result.fetchall()
    return [{"name": product[0], "size": product[1], "TotalSold": product[2]} for product in products]

@router.get("/top-selling-stores")
async def get_top_selling_stores(session: AsyncSession = Depends(get_session)):
    query = text("""
        SELECT
            stores.storeID,
            stores.zipcode,
            stores.State_abbr,
            stores.latitude,
            stores.longitude,
            stores.city,
            stores.state,
            SUM(orders.total) AS TotalRevenue
        FROM public.stores
        INNER JOIN public.orders ON stores.storeID = orders.storeID
        GROUP BY stores.storeID, stores.zipcode, stores.State_abbr, stores.latitude, stores.longitude, stores.city, stores.state
        ORDER BY TotalRevenue DESC;
    """)
    result = await session.execute(query)
    stores = result.fetchall()
    return [
        {
            "storeID": store[0],
            "zipcode": store[1],
            "State_abbr": store[2],
            "latitude": store[3],
            "longitude": store[4],
            "city": store[5],
            "state": store[6],
            "TotalRevenue": store[7]
        } for store in stores
    ]

@router.get('/')
def read_root():
    return {"Hello": "World"}