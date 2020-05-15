import os
import sqlite3
import typing

from dotenv import load_dotenv

from Utilitary.logger import log

load_dotenv(dotenv_path=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env')))
DATABASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', os.getenv('DATABASE_PATH')))
DATABASE_TABLE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', os.getenv('DATABASE_TABLE_PATH')))
log('Database::_', f"Database path -> {DATABASE_PATH}")


def fetch_one(sql: str, parameters: typing.Optional[typing.Union[list, dict, tuple]]) -> typing.Optional[tuple]:
    """
    Retrieve one row of a table according to an SQL query. Handle parameter substitution

    :param sql: str | The SQL query to execute
    :param parameters: Optional[list, dict, tuple] | The query's parameters
    :return: Optional[tuple] | A tuple  containing the data or None if no data was found
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


def fetch_all(sql: str, parameters: typing.Optional[typing.Union[list, dict, tuple]]) \
        -> typing.Optional[typing.List[tuple]]:
    """
    Retrieve all the rows of a table according to an SQL query. Handle parameter substitution

    :param sql: str | The SQL query to execute
    :param parameters: Optional[list, dict, tuple] | The query's parameters
    :return: Optional[List[tuple]] | A list of tuple containing the data or None if no data was found
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


def execute_order(sql: str, parameters: typing.Optional[typing.Union[list, dict, tuple]]) -> bool:
    """
    Execute an SQL statement. Handle parameter substitution

    :param sql: str | The SQL statement to execute
    :param parameters: Optional[list, dict, tuple] | The statement's parameters
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
