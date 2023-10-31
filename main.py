from enum import Enum
from typing import Optional, List

from fastapi import Depends, FastAPI, Query
from pydantic import BaseModel
import sqlite3
import inspect
import redis.asyncio as redis
from contextlib import asynccontextmanager
import os

import uvicorn
from limiter import CoreRateLimiter

from limiter.limiter import RateLimiter


@asynccontextmanager
async def lifespan(app: FastAPI):
    r = redis.from_url(f"redis://{os.environ['REDIS_HOST']}:{os.environ['REDIS_PORT']}", encoding="utf8")
    await CoreRateLimiter.init(r)
    yield
    await CoreRateLimiter.close()


app = FastAPI(lifespan=lifespan)


class Status(Enum):
    Active = "active"
    NotStarted = "not_started"
    Terminated = "terminated"


class Employee(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    phone: Optional[str]
    department: str
    position: str
    location: str
    status: Status
    org_id: int


@app.get("/search", dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def search(
    query: str = Query(..., title="Search Query"),
    status: List[Status] = Query(None, title="Status Filter"),
    location: List[str] = Query(None, title="Locations Filter"),
    company: List[str] = Query(None, title="Companies Filter"),
    department: List[str] = Query(None, title="Departments Filter"),
    position: List[str] = Query(None, title="Positions Filter"),
):
    db_path = "data/employees.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query_stmt = """
        SELECT * FROM employees
        WHERE
    """

    if query:
        query_stmt += f"(first_name LIKE '%{query.lower()}%' OR last_name LIKE '%{query.lower()}%')"
    if status:
        query_stmt += f" AND status IN ("
        for value in status:
            query_stmt += f"'{value.value}',"
        query_stmt = query_stmt[:-1]
        query_stmt += ")"
    if location:
        query_stmt += get_filter_string(location)
    if company:
        query_stmt += get_filter_string(company)
    if department:
        query_stmt += get_filter_string(department)
    if position:
        query_stmt += get_filter_string(position)

    cursor.execute(query_stmt)

    result: List[Employee] = cursor.fetchall()

    conn.close()

    return result


def get_filter_string(column_filter: List[str]):
    # Hacky approach to get the column name
    frame = inspect.currentframe()
    frame = inspect.getouterframes(frame)[1]
    string = inspect.getframeinfo(frame[0]).code_context[0].strip()
    args = string[string.find('(') + 1:-1].split(',')
    names = []
    for i in args:
        if i.find('=') != -1:
            names.append(i.split('=')[1].strip())
        else:
            names.append(i)
    column_name = names[0]

    query_stmt = f" AND {column_name} IN ("
    for value in column_filter:
        query_stmt += f"'{value}',"
    query_stmt = query_stmt[:-1]
    query_stmt += ")"

    return query_stmt


if __name__ == "__main__":
    uvicorn.run("main:app", host=os.environ['SERVER_HOST'], port=int(os.environ['SERVER_PORT']), reload=True)
