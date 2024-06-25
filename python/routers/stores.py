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
from datetime import date



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
async def get_top_selling_stores(
    start_date: date = date(2020, 1, 1),
    end_date: date = date(2023, 1, 1),
    session: AsyncSession = Depends(get_session)
):
    query = text("""
        SELECT
            stores.storeID,
            SUM(orders.total) AS TotalRevenue
        FROM public.stores
        INNER JOIN public.orders ON stores.storeID = orders.storeID
        WHERE orders.orderdate BETWEEN :start_date AND :end_date
        GROUP BY stores.storeID
        ORDER BY TotalRevenue DESC;
    """)
    result = await session.execute(query, {"start_date": start_date, "end_date": end_date})
    stores = result.fetchall()
    return [
        {
            "storeid": store[0],
            "TotalRevenue": store[1]
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
    period: str = Query(..., regex="^(Day|Week|Month|Quarter)$"),
    session: AsyncSession = Depends(get_session)
):
    query = text("""
        WITH SalesData AS (
            SELECT 
                storeid,
                DATE_TRUNC(
                    CASE
                        WHEN :period = 'Day' THEN 'day' 
                        WHEN :period = 'Week' THEN 'week'
                        WHEN :period = 'Month' THEN 'month'
                        ELSE 'quarter'
                    END, orderdate
                ) AS period_date,
                EXTRACT(YEAR FROM orderdate) AS year,
                EXTRACT(QUARTER FROM orderdate) AS quarter,
                COUNT(orderid) AS number_of_sales
            FROM 
                orders
            WHERE
                orderdate >= CASE
                                WHEN :period = 'Day' THEN DATE '2022-12-31' - INTERVAL '12 DAYS' 
                                WHEN :period = 'Week' THEN DATE '2022-12-31' - INTERVAL '12 WEEKS'
                                WHEN :period = 'Month' THEN DATE '2022-12-31' - INTERVAL '12 MONTHS'
                                ELSE '1900-01-01'
                            END
            GROUP BY 
                storeid, period_date, year, quarter
        )
        SELECT
            storeid,
            CASE
                WHEN :period = 'Day' THEN TO_CHAR(period_date, 'YYYY-MM-DD')
                WHEN :period = 'Week' THEN TO_CHAR(period_date, 'IYYY-IW')
                WHEN :period = 'Month' THEN TO_CHAR(period_date, 'YYYY-MM')
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

    result = await session.execute(query, {"period": period})
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

@router.get('/stores')
def read_root():
    return {"Hello": "World123"}