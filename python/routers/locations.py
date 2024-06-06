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

router = APIRouter()

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

@router.get('/locations')
def read_root():
    return {"Hello": "World111213"}