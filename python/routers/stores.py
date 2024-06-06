import logging
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
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from sqlalchemy import select
from pydantic import BaseModel



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
    
@router.get('/sales-by-store/{storeid}/')
async def get_sales_by_store(storeid: str, session: AsyncSession = Depends(get_session)):
    query = text("""
        SELECT 
            EXTRACT(YEAR FROM orderdate) AS year,
            CONCAT('Q', EXTRACT(QUARTER FROM orderdate)) AS quarter,
            COUNT(orderid) AS number_of_sales
        FROM 
            orders
        WHERE 
            storeid = :storeid
        GROUP BY 
            EXTRACT(YEAR FROM orderdate),
            EXTRACT(QUARTER FROM orderdate)
        ORDER BY 
            year,
            quarter;
    """)
    result = await session.execute(query, {'storeid': storeid})
    sales_data = result.fetchall()
    return [
        {
            "year": sale[0],
            "quarter": sale[1],
            "number_of_sales": sale[2]
        }
        for sale in sales_data
    ]
    
@router.get("/revenue-by-store/{storeid}")
async def get_sales_by_store(storeid: str, session: AsyncSession = Depends(get_session)):
    query = text("""
        SELECT 
            EXTRACT(YEAR FROM orderdate) AS year,
            CONCAT('Q', EXTRACT(QUARTER FROM orderdate)) AS quarter,
            SUM(total) AS total_revenue
        FROM 
            orders
        WHERE 
            storeid = :storeid
        GROUP BY 
            EXTRACT(YEAR FROM orderdate),
            EXTRACT(QUARTER FROM orderdate)
        ORDER BY 
            year,
            quarter;
    """)
    
    result = await session.execute(query, {"storeid": storeid})
    sales_data = result.fetchall()
    if not sales_data:
        raise HTTPException(status_code=404, detail="No sales data found for this store.")
    return [
        {
            "year": sale[0],
            "quarter": sale[1],
            "total_revenue": sale[2]
        }
        for sale in sales_data
    ]    

@router.get('/stores')
def read_root():
    return {"Hello": "World123"}