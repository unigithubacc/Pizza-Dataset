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
from typing import Optional

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

@router.get("/products/revenue-over-time")
async def get_revenue_over_time(session: AsyncSession = Depends(get_session)):
    query = text("""
        SELECT 
            p.name,
            DATE_TRUNC('month', o.orderDate) AS month,
            SUM(o.total) AS revenue
        FROM 
            products p
        JOIN 
            order_items oi ON p.sku = oi.sku
        JOIN 
            orders o ON oi.orderid = o.orderid
        GROUP BY 
            p.name, DATE_TRUNC('month', o.orderDate)
        ORDER BY 
            month;
    """)
    result = await session.execute(query)
    revenue_data = result.fetchall()
    return [
        {"name": row[0], "month": row[1], "revenue": row[2]}
        for row in revenue_data
    ]

@router.get("/products/top-selling-products")
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

@router.get("/sales-distribution")
async def get_sales_distribution(
    year: Optional[int] = None, 
    quarter: Optional[str] = None, 
    month: Optional[int] = None, 
    session: AsyncSession = Depends(get_session)
):
    base_query = """
        SELECT 
            p.Category, 
            SUM(o.total) AS TotalSales
        FROM 
            orders o
        JOIN 
            order_items oi ON o.orderID = oi.orderID
        JOIN 
            products p ON oi.SKU = p.SKU
    """
    
    filters = []
    params = {}

    if year is not None:
        filters.append("EXTRACT(YEAR FROM o.OrderDate) = :year")
        params["year"] = year

    if quarter and quarter != "All":
        if quarter == "Q1":
            filters.append("EXTRACT(MONTH FROM o.OrderDate) IN (1, 2, 3)")
        elif quarter == "Q2":
            filters.append("EXTRACT(MONTH FROM o.OrderDate) IN (4, 5, 6)")
        elif quarter == "Q3":
            filters.append("EXTRACT(MONTH FROM o.OrderDate) IN (7, 8, 9)")
        elif quarter == "Q4":
            filters.append("EXTRACT(MONTH FROM o.OrderDate) IN (10, 11, 12)")

    if month is not None:
        year_from_month = 2020 + (month - 1) // 12  # Calculate year based on month slider value
        month_in_year = (month - 1) % 12 + 1  # Calculate actual month within the year
        filters.append("EXTRACT(YEAR FROM o.OrderDate) = :year_from_month")
        filters.append("EXTRACT(MONTH FROM o.OrderDate) = :month_in_year")
        params["year_from_month"] = year_from_month
        params["month_in_year"] = month_in_year

    if filters:
        base_query += " WHERE " + " AND ".join(filters)

    base_query += " GROUP BY p.Category;"

    query = text(base_query)
    result = await session.execute(query, params)
    sales_distribution = result.fetchall()
    
    sales_distribution_list = [
        {"category": row[0], "total_sold": row[1]} for row in sales_distribution
    ]
    
    return sales_distribution_list

@router.get("/products/revenue-by-size")
async def get_revenue_by_size(
    year: Optional[int] = None,
    quarter: Optional[str] = None,
    month: Optional[int] = None,
    session: AsyncSession = Depends(get_session)
):
    base_query = """
        SELECT 
            p.size,
            SUM(o.total) AS revenue
        FROM 
            products p
        JOIN 
            order_items oi ON p.sku = oi.sku
        JOIN 
            orders o ON oi.orderid = o.orderid
    """
    
    filters = []
    params = {}

    if year is not None:
        filters.append("EXTRACT(YEAR FROM o.OrderDate) = :year")
        params["year"] = year

    if quarter and quarter != "All":
        if quarter == "Q1":
            filters.append("EXTRACT(MONTH FROM o.OrderDate) IN (1, 2, 3)")
        elif quarter == "Q2":
            filters.append("EXTRACT(MONTH FROM o.OrderDate) IN (4, 5, 6)")
        elif quarter == "Q3":
            filters.append("EXTRACT(MONTH FROM o.OrderDate) IN (7, 8, 9)")
        elif quarter == "Q4":
            filters.append("EXTRACT(MONTH FROM o.OrderDate) IN (10, 11, 12)")

    if month is not None:
        year_from_month = 2020 + (month - 1) // 12
        month_in_year = (month - 1) % 12 + 1
        filters.append("EXTRACT(YEAR FROM o.OrderDate) = :year_from_month")
        filters.append("EXTRACT(MONTH FROM o.OrderDate) = :month_in_year")
        params["year_from_month"] = year_from_month
        params["month_in_year"] = month_in_year

    if filters:
        base_query += " WHERE " + " AND ".join(filters)

    base_query += " GROUP BY p.size;"

    query = text(base_query)
    result = await session.execute(query, params)
    revenue_by_size = result.fetchall()
    
    return [
        {"size": row[0], "revenue": row[1]}
        for row in revenue_by_size
    ]

@router.get('/products')
def read_root():
    return {"Hello": "World456"}
