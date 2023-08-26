import os
import pathlib
import sqlite3
import uuid

import pandas as pd


def delete_and_insert(
    df: pd.DataFrame,
    table_name: str,
    database_connection: sqlite3.Connection,
    key_column: str,
    insert_columns: list[str],
    schema: str | None = None,
) -> None:
    """Perform DELETE & INSERT on a SQLITE table from a DataFrame.
    Constructs an INSERT … ON CONFLICT statement, uploads the DataFrame to a
    temporary table, and then executes the INSERT.
    Parameters
    ----------
    data_frame : pandas.DataFrame
        The DataFrame to be upserted.
    table_name : str
        The name of the target table.
    engine : sqlalchemy.engine.Engine
        The SQLAlchemy Engine to use.
    schema : str, optional
        The name of the schema containing the target table.
    key_columns : list of str, optional
        A list of the column name(s) on which to match. If omitted, the
        primary key columns of the target table will be used.
    """
    table_spec = ""
    if schema:
        table_spec += '"' + schema.replace('"', '""') + '".'
    table_spec += '"' + table_name.replace('"', '""') + '"'

    all_columns = list(set([key_column] + insert_columns))

    keys = df[key_column].tolist()
    keys_str = ",".join([str(x) for x in keys])

    where_statement = f"WHERE {key_column} IN ({keys_str})"

    del_sql = f"""DELETE 
                FROM {table_spec}
                {where_statement} 
                ;"""

    with database_connection as conn:
        conn.execute(del_sql)
        df[all_columns].to_sql(
            name=table_name,
            con=conn,
            if_exists="append",
            index=False,
        )


def upsert_df(
    df: pd.DataFrame,
    table_name: str,
    database_connection: sqlite3.Connection,
    key_columns: list[str],
    insert_columns: list[str],
    schema: str | None = None,
) -> None:
    """
    Perform an "upsert" on a SQLITE table from a DataFrame.
    Constructs an INSERT … ON CONFLICT statement, uploads the DataFrame to a
    temporary table, and then executes the INSERT.
    Parameters
    ----------
    data_frame : pandas.DataFrame
        The DataFrame to be upserted.
    table_name : str
        The name of the target table.
    engine : sqlalchemy.engine.Engine
        The SQLAlchemy Engine to use.
    schema : str, optional
        The name of the schema containing the target table.
    key_columns : list of str, optional
        A list of the column name(s) on which to match. If omitted, the
        primary key columns of the target table will be used.
    """
    table_spec = ""
    if schema:
        table_spec += '"' + schema.replace('"', '""') + '".'
    table_spec += '"' + table_name.replace('"', '""') + '"'

    all_columns = list(set(key_columns + insert_columns))

    insert_col_list = ", ".join([f'"{col_name}"' for col_name in all_columns])

    temp_table = f"temp_{uuid.uuid4().hex[:6]}"
    sql_query = f"""INSERT OR IGNORE INTO {table_spec} ({insert_col_list})
                SELECT {insert_col_list} FROM {temp_table}
                ;
                """

    with database_connection as conn:
        conn.execute(f"DROP TABLE IF EXISTS {temp_table}")
        conn.execute(
            f"""CREATE TEMPORARY TABLE {temp_table} 
            AS SELECT * FROM {table_spec} WHERE false"""
        )
        df[all_columns].to_sql(
            temp_table,
            con=conn,
            if_exists="append",
            index=False,
        )
        conn.execute(sql_query)
        conn.execute(f"DROP TABLE IF EXISTS {temp_table}")


def query_article(article_id: int) -> pd.DataFrame:
    query_str = f""" SELECT * 
        FROM articles
        WHERE id = {article_id} 
        ;
        """
    # Connect to the SQLite database
    with sqlite3.connect(DATABASE_PATH) as conn:
        # Use pandas to run the SQL query and return results as a DataFrame
        df = pd.read_sql_query(query_str, conn)
    return df


def query_type(type: str, page_number: int, items_per_page: int) -> pd.DataFrame:
    offset = (page_number - 1) * items_per_page
    query_str = f"""SELECT {type}.RANK, articles.*
        FROM {type}
        LEFT JOIN articles
            USING (id)
        ORDER BY {type}.rank ASC 
        LIMIT {items_per_page} OFFSET {offset}
        ;
        """
    # Connect to the SQLite database
    with sqlite3.connect(DATABASE_PATH) as conn:
        # Use pandas to run the SQL query and return results as a DataFrame
        df = pd.read_sql_query(query_str, conn)
    return df


DB_DIR = pathlib.Path(__file__).resolve().parent
DATABASE_PATH = f"{DB_DIR}/data.db"
SETUP_SQL_PATH = f"{DB_DIR}/create_db.sql"


if not os.path.exists(DATABASE_PATH):
    print("creating db with empty tables")
    # Read the SQL commands from the create.sql file
    with open(SETUP_SQL_PATH, "r") as file:
        sql_commands = file.read()
    connection = sqlite3.connect(DATABASE_PATH)
    connection.executescript(sql_commands)
    connection.commit()
    connection.close()
connection = sqlite3.connect(DATABASE_PATH)
