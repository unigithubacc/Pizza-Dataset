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
from typing import List
from fastapi import HTTPException
from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from pydantic import BaseModel
import logging
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from typing import List, Optional, AsyncGenerator
from sqlalchemy import text
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

class AvgSalesPerHour(BaseModel):
    hour: int
    avg_sales_per_hour: float

class AvgOrdersPerDay(BaseModel):
    day_of_week: str
    avg_orders: float

# Customer Distribution by Location
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

@router.get("/sales/average_per_hour/", response_model=List[AvgSalesPerHour])
async def get_avg_sales_per_hour(storeid: str, session: AsyncSession = Depends(get_session)):
    query = text("""
        SELECT
            EXTRACT(HOUR FROM orderdate AT TIME ZONE 'UTC' AT TIME ZONE 'GMT-7') AS hour,
            COUNT(*) / COUNT(DISTINCT orderdate::DATE) AS avg_sales_per_hour
        FROM orders
        WHERE storeid = :storeid
        GROUP BY hour
        ORDER BY hour
    """)
    result = await session.execute(query, {"storeid": storeid})
    rows = result.fetchall()
    return [
        {
            "hour": row[0],  # Access by index
            "avg_sales_per_hour": row[1]  # Access by index
        }
        for row in rows
    ]

@router.get("/sales/avg_orders_per_day/", response_model=List[AvgOrdersPerDay])
async def get_avg_orders_per_day(storeid: str, session: AsyncSession = Depends(get_session)):
    try:
        query = text("""
            SELECT 
                TO_CHAR(orderDate, 'Day') AS DayOfWeek,
                COUNT(orderID)::float / COUNT(DISTINCT DATE(orderDate)) AS AvgOrders
            FROM orders
            WHERE storeID = :storeid
            GROUP BY DayOfWeek
            ORDER BY CASE
                WHEN TO_CHAR(orderDate, 'Day') = 'Sunday   ' THEN 1
                WHEN TO_CHAR(orderDate, 'Day') = 'Monday   ' THEN 2
                WHEN TO_CHAR(orderDate, 'Day') = 'Tuesday  ' THEN 3
                WHEN TO_CHAR(orderDate, 'Day') = 'Wednesday' THEN 4
                WHEN TO_CHAR(orderDate, 'Day') = 'Thursday ' THEN 5
                WHEN TO_CHAR(orderDate, 'Day') = 'Friday   ' THEN 6
                WHEN TO_CHAR(orderDate, 'Day') = 'Saturday ' THEN 7
            END
        """)
        result = await session.execute(query, {"storeid": storeid})
        rows = result.fetchall()

        if not rows:
            raise HTTPException(status_code=404, detail="No data found for the given store ID")

        return [
            {
                "day_of_week": row[0].strip(),
                "avg_orders": float(row[1])
            }
            for row in rows
        ]
    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        raise HTTPException(status_code=500, detail=error_msg)

@router.get('/customers')
def read_root():
    return {"Hello": "World789"}