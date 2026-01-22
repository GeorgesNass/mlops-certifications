'''
__author__ = "Georges Nassopoulos"
__copyright__ = None
__version__ = "1.0.0"
__email__ = "georges.nassopoulos@gmail.com"
__status__ = "Dev"
__desc__ = "FastAPI service to manage dynamic MySQL tables using SQLAlchemy within a Kubernetes environment."
'''

from __future__ import annotations

import os
from typing import Any, Dict

from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import Column, Integer, MetaData, String, Table, create_engine, text
from sqlalchemy.exc import SQLAlchemyError

## -----------------------------------------------------------------------------
## FastAPI app initialization
## -----------------------------------------------------------------------------
app = FastAPI()

## -----------------------------------------------------------------------------
## MySQL configuration (environment variables injected by Kubernetes)
## -----------------------------------------------------------------------------
MYSQL_USER: str = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "root")
MYSQL_HOST: str = os.getenv("MYSQL_HOST", "mysql")

MYSQL_PORT: str = (
    os.getenv("MYSQL_SERVICE_PORT_MYSQL")
    or os.getenv("MYSQL_SERVICE_PORT")
    or os.getenv("MYSQL_PORT", "3307")
)

if "tcp://" in MYSQL_PORT:
    MYSQL_PORT = MYSQL_PORT.split(":")[-1]

MYSQL_DATABASE: str = os.getenv("MYSQL_DATABASE", "mydb")

## -----------------------------------------------------------------------------
## SQLAlchemy engine + metadata
## -----------------------------------------------------------------------------
## Use mysqlclient driver (mysqldb) because requirements.txt includes mysqlclient
CONN_STRING: str = (
    f"mysql+mysqldb://{MYSQL_USER}:{MYSQL_PASSWORD}"
    f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
)

mysql_engine = create_engine(CONN_STRING)
metadata = MetaData()

## -----------------------------------------------------------------------------
## Pydantic models
## -----------------------------------------------------------------------------
class TableSchema(BaseModel):
    """
    Schema definition for creating a table dynamically.

    Attributes:
        table_name: Name of the table to create.
        columns: Mapping {column_name: column_type_as_string}
            Examples:
                {"id": "int", "name": "string(120)"}
    """

    table_name: str
    columns: Dict[str, str]


## -----------------------------------------------------------------------------
## Helpers
## -----------------------------------------------------------------------------
def parse_column_type(type_str: str) -> Any:
    """
    Parse a column type string into a SQLAlchemy type.

    Supported values:
        - "string" or "string(n)" -> String(n) (default n=255)
        - Anything containing "int" -> Integer()

    Args:
        type_str: Column type as a string (e.g., "string(50)", "int")

    Returns:
        A SQLAlchemy type instance

    Raises:
        ValueError: If the type is not supported
    """
    if type_str.lower().startswith("string"):
        length = 255
        if "(" in type_str and ")" in type_str:
            length_str = type_str[type_str.find("(") + 1 : type_str.find(")")]
            length = int(length_str)
        return String(length)

    if "int" in type_str.lower():
        return Integer()

    raise ValueError(f"Unsupported type: {type_str}")


## -----------------------------------------------------------------------------
## Health endpoint (used by Kubernetes liveness probe)
## -----------------------------------------------------------------------------
@app.get("/health")
async def health() -> Dict[str, str]:
    """
    Lightweight health endpoint.

    Returns:
        {"status": "ok"}
    """
    return {"status": "ok"}


## -----------------------------------------------------------------------------
## API endpoints
## -----------------------------------------------------------------------------
@app.get("/tables")
async def get_tables() -> Dict[str, Any]:
    """
    List existing tables in the configured MySQL database.

    Returns:
        A dict with key "database" containing the list of table names.
    """
    with mysql_engine.connect() as connection:
        results = connection.execute(text("SHOW TABLES;"))
        return {"database": [str(row[0]) for row in results.fetchall()]}


@app.put("/table")
async def create_table(schema: TableSchema) -> Dict[str, Any]:
    """
    Create a new table dynamically based on the provided schema.

    Args:
        schema: Table schema (table name + columns mapping)

    Returns:
        A dict containing either a success message or an error message.
    """
    try:
        columns = [
            Column(col_name, parse_column_type(col_type))
            for col_name, col_type in schema.columns.items()
        ]

        table = Table(schema.table_name, metadata, *columns, extend_existing=True)
        metadata.create_all(mysql_engine, tables=[table], checkfirst=False)

        return {"message": f"Table '{schema.table_name}' successfully created."}

    except SQLAlchemyError as exc:
        return {"error_msg": str(exc)}
    except Exception as exc:
        return {"error_msg": f"Unexpected error: {exc}"}
