import sqlite3
import typing
from Utilitary.logger import log
import os
from dotenv import load_dotenv


load_dotenv(dotenv_path=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env')))
DATABASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', os.getenv('DATABASE_PATH')))
DATABASE_TABLE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', os.getenv('DATABASE_TABLE_PATH')))
log('Database::_', f"Database path -> {DATABASE_PATH}")

# Special type for SQL functions' parameters
SqlParameterType = typing.Optional[typing.Union[list, dict, tuple]]


def fetch_one(sql: str, parameters: SqlParameterType = None) -> typing.Optional[tuple]:
    """
    Retrieve one row of a table according to an SQL query. Handle parameter substitution

    :param sql: str | The SQL query to execute
    :param parameters: list, dict, tuple or None | The query's parameters
    :return: tuple or None | A tuple  containing the data or None if no data was found
    """
    if parameters is None:
        parameters = []
    con = sqlite3.connect(DATABASE_PATH)
    cursor = con.cursor()
    try:
        cursor.execute(sql, parameters)
        line = cursor.fetchone()
        return line
    except Exception as e:
        log('Database::fetch_one', f"{type(e).__name__} - {e} - SQL : `{sql}` - Parameters : `{parameters}`")
        return None
    finally:
        cursor.close()
        con.close()


def fetch_all(sql: str, parameters: SqlParameterType = None) -> typing.Optional[typing.List[tuple]]:
    """
    Retrieve all the rows of a table according to an SQL query. Handle parameter substitution

    :param sql: str | The SQL query to execute
    :param parameters: list, dict, tuple or None | The query's parameters
    :return: List[tuple] or None | A list of tuple containing the data or None if no data was found
    """
    if parameters is None:
        parameters = []
    con = sqlite3.connect(DATABASE_PATH)
    cursor = con.cursor()
    try:
        cursor.execute(sql, parameters)
        lines = cursor.fetchall()
        return lines if len(lines) != 0 else None
    except Exception as e:
        log('Database::fetch_all', f"{type(e).__name__} - {e} - SQL : `{sql}` - Parameters : `{parameters}`")
        return None
    finally:
        cursor.close()
        con.close()


def execute_order(sql: str, parameters: SqlParameterType = None) -> bool:
    """
    Execute an SQL statement. Handle parameter substitution

    :param sql: str | The SQL statement to execute
    :param parameters: list, dict, tuple or None | The statement's parameters
    :return: bool | True if the order didn't raise any error, else False
    """
    if parameters is None:
        parameters = []
    con = sqlite3.connect(DATABASE_PATH)
    cursor = con.cursor()
    try:
        cursor.execute(sql, parameters)
        con.commit()
        return True
    except Exception as e:
        log('Database::execute_order', f"{type(e).__name__} - {e} - SQL : `{sql}` - Parameters : `{parameters}`")
        return False
    finally:
        cursor.close()
        con.close()


def __create_database_table():
    """
    Execute all the SQL query written inside the `sql_script_path` variable
    which should be the path to an `.sql` file listing all the table of the database
    """
    sql_file = open(DATABASE_TABLE_PATH, 'r')
    con = sqlite3.connect(DATABASE_PATH)
    cursor = con.cursor()
    try:
        cursor.executescript(sql_file.read())
    except Exception as e:
        log('Database::create_database_table', f"{type(e).__name__} - {e}")
    finally:
        cursor.close()
        con.close()
        sql_file.close()


if __name__ == '__main__':
    print(DATABASE_PATH)
    print(DATABASE_TABLE_PATH)
    __create_database_table()
