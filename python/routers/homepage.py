from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from sqlalchemy import Column, Integer, String, Text, bindparam
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
from datetime import date

DATABASE_URL = "postgresql+asyncpg://postgres:ProLab895+@localhost:5432/pizza"

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

router = APIRouter()

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
        
class YearQuarterParams(BaseModel):
    year: Optional[int] = Query(None, gt=2000, lt=9999)
    quarter: Optional[int] = Query(None, gt=0, lt=5)
        

@router.get("/dashboard-overview")
async def get_dashboard_overview(session: AsyncSession = Depends(get_session)):
    queries = {
        "TotalRevenue": "SELECT SUM(total) AS TotalRevenue FROM public.orders;",
        "TotalOrders": "SELECT COUNT(orderID) AS TotalOrders FROM public.orders;",
        "TotalCustomers": "SELECT COUNT(DISTINCT customerID) AS TotalCustomers FROM public.customers;",
        "TotalStores": "SELECT COUNT(storeID) AS TotalStores FROM public.stores;",
        "PizzasSold": "SELECT SUM(nItems) AS PizzasSold FROM public.orders;",
        "NumberOfProducts": "SELECT COUNT(DISTINCT Name) AS NumberOfProducts FROM public.products;",
        "MostPopularProduct": """
            SELECT products.Name 
            FROM public.order_items 
            JOIN public.products ON order_items.SKU = products.SKU 
            GROUP BY products.Name 
            ORDER BY COUNT(order_items.SKU) DESC 
            LIMIT 1;
        """,
        "AverageOrderValue": "SELECT AVG(total) AS AverageOrderValue FROM public.orders;",
    }

    results = {}

    for key, query in queries.items():
        result = await session.execute(text(query))
        results[key] = result.scalar()

    return results


@router.get("/revenue-ranking/")
async def get_revenue_ranking(session: AsyncSession = Depends(get_session)):

    query = text("""
    WITH revenue_per_store AS (
        SELECT 
            storeid,
            EXTRACT(YEAR FROM orderdate) AS year,
            EXTRACT(QUARTER FROM orderdate) AS quarter,
            SUM(total) AS total_revenue
        FROM 
            orders
        GROUP BY 
            storeid,
            EXTRACT(YEAR FROM orderdate),
            EXTRACT(QUARTER FROM orderdate)
    ),
    store_ranking AS (
        SELECT 
            storeid,
            year,
            quarter,
            total_revenue,
            RANK() OVER (PARTITION BY year, quarter ORDER BY total_revenue DESC) AS rank
        FROM 
            revenue_per_store
    )
    SELECT 
        year,
        CONCAT('Q', quarter) AS quarter,
        storeid,
        total_revenue,
        rank
    FROM 
        store_ranking
    ORDER BY 
        year,
        quarter,
        rank
    """)


    result = await session.execute(query)
    rankings = result.fetchall()

    if not rankings:
        raise HTTPException(status_code=404, detail="No data found.")

    return [
        dict(year=row[0], quarter=row[1], storeid=row[2], total_revenue=row[3], rank=row[4])
        for row in rankings
    ]

@router.get("/pizzerankings/")
async def get_pizza_rankings(session: AsyncSession = Depends(get_session)):
    query = text("""
    WITH pizza_sales AS (
        SELECT 
            products.name,
            EXTRACT(YEAR FROM orders.orderdate) AS year,
            EXTRACT(QUARTER FROM orders.orderdate) AS quarter,
            COUNT(order_items.orderid) AS number_of_sales
        FROM 
            order_items
        JOIN 
            products ON order_items.sku = products.sku
        JOIN
            orders ON order_items.orderid = orders.orderid
        GROUP BY 
            products.name, 
            EXTRACT(YEAR FROM orders.orderdate),
            EXTRACT(QUARTER FROM orders.orderdate)
    ),
    pizza_ranking AS (
        SELECT 
            name,
            year,
            quarter,
            number_of_sales,
            RANK() OVER (PARTITION BY year, quarter ORDER BY number_of_sales DESC) AS rank
        FROM 
            pizza_sales
    )
    SELECT 
        name,
        year,
        quarter,
        number_of_sales,
        rank
    FROM 
        pizza_ranking
    ORDER BY 
        year,
        quarter,
        rank;
    """)
    
    result = await session.execute(query)
    rankings = result.fetchall()

    if not rankings:
        raise HTTPException(status_code=404, detail="Keine Daten gefunden.")

    return [
        {"name": row[0], "year": row[1], "quarter": row[2], "number_of_sales": row[3], "rank": row[4]}
        for row in rankings
    ]

@router.get('/dashboard')
def read_root():
    return {"Hello": "World123"}
