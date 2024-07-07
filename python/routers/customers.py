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

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


router = APIRouter()

# Costumer Distribution by Location
@router.get("/customer-locations")
async def get_customer_locations(min_orders: int = Query(1, description="Minimum number of orders"), session: AsyncSession = Depends(get_session)):
    query = text("""
        SELECT 
            latitude, 
            longitude
        FROM 
            customers c
        JOIN (
            SELECT customerID
            FROM orders
            GROUP BY customerID
            HAVING COUNT(*) > :min_orders
        ) o ON c.customerID = o.customerID;     
    """)
    result = await session.execute(query, {"min_orders": min_orders})
    customer_locations = result.fetchall()
    return [{"latitude": loc[0], "longitude": loc[1]} for loc in customer_locations]

@router.get("/customer_locations/{storeid}")
async def get_customer_locations(storeid: str, min_orders: int = Query(1, description="Minimum number of orders"), session: AsyncSession = Depends(get_session)):
    query = text("""
        SELECT 
            c.latitude, 
            c.longitude
        FROM 
            customers c
        JOIN (
            SELECT customerID
            FROM orders
            WHERE storeID = :storeid
            GROUP BY customerID
            HAVING COUNT(*) >= :min_orders
        ) o ON c.customerID = o.customerID;
    """)
    result = await session.execute(query, {"storeid": storeid, "min_orders": min_orders})
    customer_locations = result.fetchall()
    return [{"latitude": loc[0], "longitude": loc[1]} for loc in customer_locations]


    # Store Locations
@router.get("/store-locations")
async def get_store_locations(session: AsyncSession = Depends(get_session)):
    query = text("""
        SELECT 
            storeID, 
            latitude, 
            longitude, 
            city, 
            state
        FROM 
            stores;
    """)
    try:
        result = await session.execute(query)
        store_locations = result.fetchall()
        store_location_list = [
            {
                "storeID": row[0], 
                "latitude": row[1], 
                "longitude": row[2], 
                "city": row[3],
                "state": row[4]
            } for row in store_locations
        ]
        return store_location_list
    except Exception as e:
        logging.error(f"Error fetching store locations: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get('/customers')
def read_root():
    return {"Hello": "World789"}