import logging
from fastapi import APIRouter, HTTPException, Query, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from sqlalchemy import Column, Integer, String, Text, tuple_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import bindparam
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
from datetime import date, timedelta



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

class SalesData(BaseModel):
    storeid: str
    period: str
    total_sales: int

class ProductRevenue(BaseModel):
    name: str
    size: str
    product_revenue: float
    number_of_orders: int

class ProductRevenueWithSize(BaseModel):
    name: str
    size: Optional[str]
    product_revenue: float
    number_of_orders: int

class ProductRevenueWithoutSize(BaseModel):
    name: str
    product_revenue: float
    number_of_orders: int
    
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

class CategoryRevenue(BaseModel):
    category: str
    product_revenue: float
    number_of_orders: int

class SizeRevenue(BaseModel):
    size: str
    product_revenue: float
    number_of_orders: int

class TotalCustomer(BaseModel):
    storeid: str
    totalcustomers: int

class ProductCount(BaseModel):
    product1: str
    product2: str
    avgfrequencyperorder: float

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
async def get_top_selling_stores(
    start_date: date = date(2020, 1, 1),
    end_date: date = date(2023, 1, 1),
    session: AsyncSession = Depends(get_session)
):
    query = text("""
        SELECT
            stores.storeID,
            SUM(orders.total) AS TotalRevenue,
            COUNT(DISTINCT orders.customerID) AS CustomerCount
        FROM public.stores
        INNER JOIN public.orders ON stores.storeID = orders.storeID
        WHERE orders.orderdate BETWEEN :start_date AND :end_date
        GROUP BY stores.storeID;
    """)
    result = await session.execute(query, {"start_date": start_date, "end_date": end_date})
    stores = result.fetchall()
    return [
        {
            "storeid": store[0],
            "TotalRevenue": store[1],
            "CustomerCount": store[2]
        } for store in stores
    ]

@router.get('/sales-by-store/')
async def get_sales_by_store(storeid: List[str] = Query(..., alias='storeid'), session: AsyncSession = Depends(get_session)):
    try:
        # Konvertiere die Liste von Strings in eine Liste von Tupeln
        storeid_tuples = [(sid,) for sid in storeid]  # Jedes Tupel enthält nur ein Element
        
        query = text("""
            SELECT 
                storeid,
                EXTRACT(YEAR FROM orderdate) AS year,
                CONCAT('Q', EXTRACT(QUARTER FROM orderdate)) AS quarter,
                COUNT(orderid) AS number_of_sales
            FROM 
                orders
            WHERE 
                storeid IN :store_ids
            GROUP BY 
                storeid,
                EXTRACT(YEAR FROM orderdate),
                EXTRACT(QUARTER FROM orderdate)
            ORDER BY 
                storeid,
                year,
                quarter;
        """).bindparams(bindparam('store_ids', expanding=True))

        result = await session.execute(query, {'store_ids': storeid_tuples})
        sales_data = result.fetchall()
        
        if not sales_data:
            raise HTTPException(status_code=404, detail="No sales data found for the specified stores.")
        
        return [
            {
                "storeid": sale[0],
                "year": sale[1],
                "quarter": sale[2],
                "number_of_sales": sale[3]
            }
            for sale in sales_data
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
@router.get("/sales-report/")
async def get_sales_report(session: AsyncSession = Depends(get_session)):
    query = text("""
        SELECT 
            storeid,
            EXTRACT(YEAR FROM orderdate) AS year,
            CONCAT('Q', EXTRACT(QUARTER FROM orderdate)) AS quarter,
            COUNT(orderid) AS number_of_sales
        FROM 
            orders
        GROUP BY 
            storeid,
            EXTRACT(YEAR FROM orderdate),
            EXTRACT(QUARTER FROM orderdate)
        ORDER BY 
            storeid,
            year,
            quarter;
    """)
    result = await session.execute(query)
    sales_data = result.fetchall()

    # Convert the list of tuples to a list of dictionaries
    sales_data_dicts = [
        {
            "storeid": row[0],
            "year": row[1],
            "quarter": row[2],
            "number_of_sales": row[3]
        }
        for row in sales_data
    ]

    return sales_data_dicts   
    
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

@router.get("/repeat-customers-report/")
async def get_repeat_customers_report(
    min_order_count: int = Query(1, alias="min_order_count"),
    session: AsyncSession = Depends(get_session)
):
    query = text(f"""
        SELECT 
            s.storeid,
            ROUND((COUNT(DISTINCT CASE WHEN sub.order_count > :min_order_count THEN o.customerid END) * 1.0 / COUNT(DISTINCT o.customerid)) * 100, 2) AS repeat_rate,
            COUNT(DISTINCT o.customerid) AS total_customers
        FROM 
            stores s
        JOIN 
            orders o ON s.storeid = o.storeid
        JOIN 
            (SELECT 
                 customerid, 
                 COUNT(orderid) AS order_count 
             FROM 
                 orders 
             GROUP BY 
                 customerid) sub 
        ON 
            o.customerid = sub.customerid
        GROUP BY 
            s.storeid
        ORDER BY 
            repeat_rate DESC;
    """)
    
    result = await session.execute(query, {'min_order_count': min_order_count})
    report_data = result.fetchall()

    # Konvertieren Sie das Ergebnis in eine Liste von Wörterbüchern
    report_data_dicts = [
        {
            "storeid": row[0],
            "repeat_rate": row[1],
            "total_customers": row[2]
        }
        for row in report_data
    ]

    return report_data_dicts

@router.get("/sales-report-time-interval/", response_model=List[SalesData])
async def get_sales_data(
    period: str = Query(..., regex="^(Day|Month|Year|Quarter)$"),
    end_date: date = Query(...),
    session: AsyncSession = Depends(get_session)
):
    # Calculate start_date based on period
    if period == 'Day':
        start_date = end_date - timedelta(days=30)
    elif period == 'Week':
        # Calculate the start of the ISO year and week
        iso_year, iso_week, _ = end_date.isocalendar()
        start_date = date.fromisocalendar(iso_year - 1, iso_week, 1)
    elif period == 'Month':
        start_date = end_date - timedelta(days=365)  # Approximately 12 months
    elif period == 'Year':
        start_date = end_date - timedelta(days=365 * 12)  # Approximately 12 years
    else:
        start_date = date(1900, 1, 1)  # Default for Quarter

    query = text("""
        WITH SalesData AS (
            SELECT 
                storeid,
                DATE_TRUNC(
                    CASE
                        WHEN :period = 'Day' THEN 'day' 
                        WHEN :period = 'Month' THEN 'month'
                        WHEN :period = 'Year' THEN 'year'
                        ELSE 'quarter'
                    END, orderdate
                ) AS period_date,
                EXTRACT(YEAR FROM orderdate) AS year,
                EXTRACT(QUARTER FROM orderdate) AS quarter,
                COUNT(orderid) AS number_of_sales
            FROM 
                orders
            WHERE
                orderdate >= :start_date
                AND orderdate <= :end_date
            GROUP BY 
                storeid, period_date, year, quarter
        )
        SELECT
            storeid,
            CASE
                WHEN :period = 'Day' THEN TO_CHAR(period_date, 'YYYY-MM-DD')
                WHEN :period = 'Month' THEN TO_CHAR(period_date, 'YYYY-MM')
                WHEN :period = 'Year' THEN TO_CHAR(period_date, 'YYYY')
                ELSE TO_CHAR(year, '0000') || '-Q' || quarter
            END AS period,
            SUM(number_of_sales) AS total_sales
        FROM
            SalesData
        GROUP BY
            storeid,
            period
        ORDER BY
            storeid,
            period;
    """)

    # Execute the query with parameters passed separately
    result = await session.execute(
        query, 
        {"period": period, "start_date": start_date, "end_date": end_date}
    )
    
    sales_data = result.fetchall()

    if not sales_data:
        raise HTTPException(status_code=404, detail="No sales data found.")

    return [
        {
            "storeid": row[0],
            "period": row[1],
            "total_sales": row[2]
        }
        for row in sales_data
    ]

@router.get("/revenue-by-store/", response_model=List[dict])
async def get_revenue_by_store(
    period: str = Query(..., regex="^(Day|Week|Month|Year|Quarter)$"),
    end_date: date = Query(...),
    session: AsyncSession = Depends(get_session)
):
    try:
        # Calculate start_date based on period
        if period == 'Day':
            start_date = end_date - timedelta(days=31)
        elif period == 'Month':
            start_date = end_date - timedelta(days=365)  # Approximately 12 months
        elif period == 'Year':
            start_date = end_date - timedelta(days=365 * 12)  # Approximately 12 years
        else:
            start_date = date(1900, 1, 1)  # Default for Quarter

        query = text("""
            WITH RevenueData AS (
                SELECT 
                    storeid,
                    DATE_TRUNC(
                        CASE
                            WHEN :period = 'Day' THEN 'day' 
                            WHEN :period = 'Week' THEN 'week'
                            WHEN :period = 'Month' THEN 'month'
                            WHEN :period = 'Year' THEN 'year'
                            ELSE 'quarter'
                        END, orderdate
                    ) AS period_date,
                    EXTRACT(YEAR FROM orderdate) AS year,
                    EXTRACT(QUARTER FROM orderdate) AS quarter,
                    SUM(total) AS total_revenue
                FROM 
                    orders
                WHERE
                    orderdate >= :start_date
                    AND orderdate <= :end_date
                GROUP BY 
                    storeid, period_date, year, quarter
            )
            SELECT
                storeid,
                CASE
                    WHEN :period = 'Day' THEN TO_CHAR(period_date, 'YYYY-MM-DD')
                    WHEN :period = 'Week' THEN TO_CHAR(period_date, 'YYYY-IW')
                    WHEN :period = 'Month' THEN TO_CHAR(period_date, 'YYYY-MM')
                    WHEN :period = 'Year' THEN TO_CHAR(period_date, 'YYYY')
                    ELSE TO_CHAR(year, '0000') || '-Q' || quarter
                END AS period,
                SUM(total_revenue) AS total_revenue
            FROM
                RevenueData
            GROUP BY
                storeid,
                period
            ORDER BY
                storeid,
                period;
        """)

        result = await session.execute(
            query, 
            {"period": period, "start_date": start_date, "end_date": end_date}
        )
        sales_data = result.fetchall()
        
        if not sales_data:
            raise HTTPException(status_code=404, detail="No revenue data found for the specified stores.")
        
        return [
            {
                "storeid": row[0],
                "period": row[1],
                "total_revenue": row[2]
            }
            for row in sales_data
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/store-products-revenue")
async def get_store_products_revenue(
    storeid: str,
    start_date: date = date(2020, 1, 1),
    end_date: date = date(2023, 1, 1),
    divide_by_size: bool = True,
    session: AsyncSession = Depends(get_session)
):
    group_by_clause = "p.name, p.size" if divide_by_size else "p.name"
    select_size_clause = "p.size" if divide_by_size else "NULL AS size"
    
    query = text(f"""
        SELECT 
            p.name,
            {select_size_clause},
            SUM(o.total) AS product_revenue,
            COUNT(oi.orderid) AS number_of_orders
        FROM 
            orders o
        JOIN 
            order_items oi ON o.orderid = oi.orderid
        JOIN 
            products p ON oi.sku = p.sku
        JOIN 
            stores s ON o.storeid = s.storeid
        WHERE 
            s.storeid = :storeid AND
            o.orderdate BETWEEN :start_date AND :end_date
        GROUP BY 
            {group_by_clause}
        ORDER BY 
            product_revenue DESC;
    """)
    
    result = await session.execute(query, {
        "storeid": storeid,
        "start_date": start_date,
        "end_date": end_date
    })
    products = result.fetchall()
    
    if divide_by_size:
        response_data = [
            {
                "name": product[0],
                "size": product[1],
                "product_revenue": product[2],
                "number_of_orders": product[3]
            } for product in products
        ]
    else:
        response_data = [
            {
                "name": product[0],
                "product_revenue": product[2],
                "number_of_orders": product[3]
            } for product in products
        ]
    
    return response_data

@router.get("/store-products-category-revenue", response_model=List[CategoryRevenue])
async def get_store_products_category_revenue(
    storeid: str,
    start_date: date = date(2020, 1, 1),
    end_date: date = date(2023, 1, 1),
    session: AsyncSession = Depends(get_session)
):
    query = text("""
        SELECT 
            p.category,
            SUM(o.total) AS product_revenue,
            COUNT(oi.orderid) AS number_of_orders
        FROM 
            orders o
        JOIN 
            order_items oi ON o.orderid = oi.orderid
        JOIN 
            products p ON oi.sku = p.sku
        JOIN 
            stores s ON o.storeid = s.storeid
        WHERE 
            s.storeid = :storeid
        GROUP BY 
            p.category
        ORDER BY 
            product_revenue DESC;
    """)
    result = await session.execute(query, {
        "storeid": storeid,
        "start_date": start_date,
        "end_date": end_date
    })
    products = result.fetchall()
    return [
        {
            "category": product[0],
            "product_revenue": product[1],
            "number_of_orders": product[2]
        } for product in products
    ]

@router.get("/store-products-size-revenue", response_model=List[SizeRevenue])
async def get_store_products_category_revenue(
    storeid: str,
    start_date: date = date(2020, 1, 1),
    end_date: date = date(2023, 1, 1),
    session: AsyncSession = Depends(get_session)
):
    query = text("""
        SELECT 
            p.size,
            SUM(o.total) AS product_revenue,
            COUNT(oi.orderid) AS number_of_orders
        FROM 
            orders o
        JOIN 
            order_items oi ON o.orderid = oi.orderid
        JOIN 
            products p ON oi.sku = p.sku
        JOIN 
            stores s ON o.storeid = s.storeid
        WHERE 
            s.storeid = :storeid
        GROUP BY 
            p.size
        ORDER BY 
            product_revenue DESC;
    """)
    result = await session.execute(query, {
        "storeid": storeid,
        "start_date": start_date,
        "end_date": end_date
    })
    products = result.fetchall()
    return [
        {
            "size": product[0],
            "product_revenue": product[1],
            "number_of_orders": product[2]
        } for product in products
    ]

@router.get("/stores/customers-count", response_model=List[TotalCustomer])
async def get_stores_customers_count(
    start_date: date = date(2020, 1, 1),
    end_date: date = date(2023, 1, 1),
    session: AsyncSession = Depends(get_session)
):
    query = text("""
        SELECT 
            s.storeid,
            COUNT(DISTINCT c.customerid) AS TotalCustomers
        FROM 
            stores s
        JOIN 
            orders o ON s.storeID = o.storeid
        JOIN 
            customers c ON o.customerid = c.customerid
        WHERE 
            o.orderdate BETWEEN :start_date AND :end_date
        GROUP BY 
            s.storeid;
    """)
    result = await session.execute(query, {"start_date": start_date, "end_date": end_date})
    stores = result.fetchall()
    return [
        {
            "storeid": stores[0],
            "totalcustomers": stores[1],
        } for stores in stores
    ]    

@router.get("/products/frequency", response_model=List[ProductCount])
async def get_products_frequency(
    storeid: str,
    start_date: date = date(2020, 1, 1),
    end_date: date = date(2023, 1, 1),
    session: AsyncSession = Depends(get_session)
):
    query = text("""
    WITH product_orders AS (
        SELECT 
            p1.Name AS Product1,
            p2.Name AS Product2,
            oi1.orderid
        FROM 
            order_items oi1
        JOIN 
            order_items oi2 ON oi1.orderid = oi2.orderid AND oi1.sku != oi2.sku
        JOIN 
            products p1 ON oi1.sku = p1.sku
        JOIN 
            products p2 ON oi2.sku = p2.sku
        JOIN 
            orders o ON oi1.orderid = o.orderID
        WHERE 
            o.storeid = :storeid
        AND o.orderdate BETWEEN :start_date AND :end_date
    ),
    total_product_orders AS (
        SELECT 
            p.name AS Product,
            COUNT(oi.orderid) AS TotalOrders
        FROM 
            orders o
        JOIN 
            order_items oi ON o.orderid = oi.orderid
        JOIN 
            products p ON oi.sku = p.sku
        JOIN 
            stores s ON o.storeid = s.storeid
        WHERE 
            o.storeid = :storeid
        AND o.orderdate BETWEEN :start_date AND :end_date
        GROUP BY 
            p.name
    )
    SELECT 
        po.Product1,
        po.Product2,
        COUNT(po.orderid) AS Frequency,
        tpo.TotalOrders,
        ROUND((COUNT(po.orderid) * 1.0 / tpo.TotalOrders), 3) AS AvgFrequencyPerOrder
    FROM 
        product_orders po
    JOIN 
        total_product_orders tpo ON po.Product1 = tpo.Product
    GROUP BY 
        po.Product1, po.Product2, tpo.TotalOrders
    ORDER BY 
        po.Product1, po.Product2 DESC;

    """)
    result = await session.execute(query, {"storeid": storeid, "start_date": start_date, "end_date": end_date})
    rows = result.fetchall()

    # Correctly iterating over the stores list and constructing dictionaries
    return [
        {
            "product1": row[0],
            "product2": row[1],
            "avgfrequencyperorder": row[4]
        }
        for row in rows
    ]

@router.get("/store-details/")
async def get_store_details(
    storeid: str,
    session: AsyncSession = Depends(get_session)
):
    query = text("""
        SELECT 
            storeid, latitude, longitude, city, state 
        FROM 
            stores 
        WHERE 
            storeid = :storeid
    """)
    
    result = await session.execute(query, {'storeid': storeid})
    store = result.fetchone()

    if store:
        return {
            "storeid": store[0],
            "latitude": store[1],
            "longitude": store[2],
            "city": store[3],
            "state": store[4]
        }
    else:
        raise HTTPException(status_code=404, detail="Store not found")

@router.get('/stores')
def read_root():
    return {"Hello": "World123"}