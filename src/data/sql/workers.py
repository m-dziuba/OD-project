import datetime
from typing import Dict, Tuple, Optional, Any, Union
import os
from itertools import product

import mysql.connector
from mysql.connector.connection import MySQLConnection
from mysql.connector.cursor import MySQLCursor
from dotenv import load_dotenv

import tables_create_queries


# TODO change SQLWorker to use __del__? Not sure if using context manager is the best way forward
class SQLWorker:
    """
    Class with basic SQL functionality like insert, execute,
    get results from cursor etc. Uses context manager.
    """

    # TODO maybe change order of methods
    def __init__(self, config: Dict[str, str]):
        self.config = config
        self.db_conn: MySQLConnection
        self.cursor: MySQLCursor

    def __enter__(self):
        self.db_conn = mysql.connector.connect(**self.config)
        self.cursor = self.db_conn.cursor(buffered=True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.cursor.close()
            self.db_conn.close()
        except mysql.connector.Error as err:
            print("Closing DB connection failed. Connection not closable")
            print(err.msg, "ERR_No:", err.errno)

    # TODO add resilience against invalid table names
    def insert_into_table(self, table: str, data: Dict[str, str]):
        """
        Insert `data` into `table`. Data has to be a `dict` where keys
        are the column names and `data[key]` is the value to be inserted into it

        :param table: Name of the table
        :param data:  Data inserted into the table
        """
        # TODO probably unnecessary but might be needed to check if data is correct
        column_names: Tuple[str, ...] = self.get_column_names(table)
        column_names_string: str = ", ".join(column_names)
        values_string: str = ", ".join(
            (f'%({column_name})s' for column_name in column_names)
        )
        insert_query: str = (f"INSERT INTO {table} "
                             f"({column_names_string}) "
                             f"VALUES ({values_string})")
        self.execute_insert_query(insert_query, data)

    def get_column_names(self, table: str) -> Tuple[str, ...]:
        """
        Get column names of given table

        :param table: table name
        :return: tuple containing names of columns
        """
        column_names_query: str = ("SELECT column_name "
                                   "FROM information_schema.columns "
                                   "WHERE table_schema='otodom' "
                                   "AND table_name='%s'")
        self.execute_read_query(column_names_query, table)
        column_names: Tuple[Any, ...] = self.get_result_from_cursor()
        return tuple(name for name in column_names if name != "id")

    def get_row_id(self, table: str, data: Dict[str, str]) -> int:
        """
        Get ID of the row inside `table` that has entries exactly like `data`.

        `data` has to be a `dict` where keys are column names and each
        `data[column_name]` is a value that has to be present in the row, under
        the given column

        :param table: name of the table that is being searched in
        :param data: dict containing column_name: value pairs
        """
        where_string: str = " AND ".join([f"{key}=%({key})s" for key in data.keys()])
        get_table_id_query: str = (f"SELECT EXISTS("
                                   f"SELECT {table}.id FROM {table} "
                                   f"WHERE {where_string})")
        self.execute_read_query(get_table_id_query, data)
        return int(self.get_result_from_cursor()[0])

    def execute_insert_query(self, query: str,
                             data: Optional[Dict[str, str]] = None):
        """
        Execute an insert query using values from `data` if present. `data` has to be a
        `dict` where keys are column names and each`data[column_name]` is a
        value that will be inserted into the row, under the given column.
        If insert fails print error message and number. Else commit the insert.

        :param query: MySQL INSERT INTO query
        :param data:
        """
        try:
            self.cursor.execute(query, data)
        except mysql.connector.Error as err:
            print("Invalid insert query")
            print(err.msg, "ERR_No:", err.errno)
        else:
            self.db_conn.commit()

    def execute_read_query(self, query: str,
                           data: Union[Dict[str, str], Tuple[str, ...], str]):
        """
        Execute read query, using `data` as query parameters. If `data` is a
        dict it has to be a `dict` where keys are column names and each
        `data[column_name]` is a value that will be inserted into the row, under
        the given column. If a tuple the order of query parameters has to be the
        same as inside the query. If a string then there can only be one query
        parameter in the query. Results have to be retrieved from the cursor.

        :param query: SELECT MySQL query
        :param data: search parameters for the query that go after WHERE, GROUP
         BY, etc.
        """
        try:
            self.cursor.execute(query, data)
        except mysql.connector.Error as err:
            print("Invalid read query")
            print(err.msg, "ERR_No:", err.errno)

    def execute_create_table_query(self, query: str, table_name: str):
        """
        Execute CREATE TABLE query. Prints table name and if the query was
        successful. If there are no errors query is committed.

        :param query: CREATE TABLE MySQL query, describing the schema
        :param table_name: Name of the table that is being created
        """
        try:
            print(f"Creating table {table_name}: ", end="")
            self.cursor.execute(query)
        except mysql.connector.Error as err:
            print(f"FAILED, {err.msg}, ERR_No:{err.errno}")
        else:
            print("OK")
            self.db_conn.commit()

    def get_result_from_cursor(self) -> Tuple[Any, ...]:
        return next(zip(*self.cursor.fetchall()))  # TODO maybe returning a list would be better


class SQLInitiator(SQLWorker):
    """
    Used to initiate the database. Can clear previous DB and create a new one,
    add all tables, fill feature tables.
    """

    def __init__(self, config: Dict[str, str]):
        super().__init__(config)
        self.tables: Dict[str, str] = tables_create_queries.get_all_tables_queries()

    def reset_db(self):
        """Drop otodom database, create new one, use it"""
        self.cursor.execute("DROP DATABASE IF EXISTS otodom;")
        self.cursor.execute("CREATE DATABASE otodom;")
        self.cursor.execute("USE otodom;")

    def init_all_tables(self):
        """Create all tables"""
        for table_name in self.tables:
            table_description: str = self.tables[table_name]
            self.execute_create_table_query(table_description, table_name)

    def fill_features_tables(self):
        """Fill all _feature tables except offer_features"""
        feature_tables: Tuple[str, str, str, str] = ("additional_features",
                                                     "safety_features",
                                                     "media_features",
                                                     "furnishing_features")
        for table in feature_tables:
            column_names: Tuple[str, ...] = self.get_column_names(table)
            columns_count: int = len(column_names)

            for combination in product([0, 1], repeat=columns_count):
                data: Dict[str, str] = {column_names[i]: str(combination[i])
                                        for i in range(columns_count)}
                self.insert_into_table(table, data)


class SQLOperator(SQLWorker):

    # TODO it doesn't seem right that those inserts have different methods
    def add_offer_features(self, offer_id: int,
                           query_data: Dict[str, Dict[str, str]]):
        """
        Insert data into offer_features table, with ids of features
        corresponding to `query_data`

        :param offer_id: ID of the offer, the insert corresponds to
        :param query_data: Dict of dicts, containing binary feature data
        """
        insert_data: Dict[str, str] = {"offer_id": str(offer_id)}
        for key in query_data.keys():
            column_name: str = key.replace("features", "id")
            insert_data[column_name] = str(self.get_row_id(key, query_data[key]))

        self.insert_into_table("offer_features", insert_data)

    def add_location(self, offer_id, data):
        # TODO perhaps split func into coordinates/geo_levels/locations
        address_data: str = data["address"]
        coordinates_data: Dict[str, str] = data["coordinates"]
        coordinates_data["offer_id"] = offer_id
        geo_levels_data: Dict[str, str] = data["geo_levels"]

        self.insert_into_table("coordinates", coordinates_data)
        geo_levels_id: int = self.get_row_id("geo_levels", geo_levels_data)
        if geo_levels_id == 0:
            self.insert_into_table("geo_levels", geo_levels_data)
            geo_levels_id = self.get_row_id("geo_levels", geo_levels_data)

        insert_data: Dict[str, str] = {
            "offer_id": offer_id,
            "address": address_data,
            "geo_levels_id": str(geo_levels_id)
        }
        self.insert_into_table("locations", insert_data)


def add_offer(oper):
    data = {
        "url": "https://adwadw.com",
        "date_created": datetime.datetime.now(),
        "date_modified": datetime.datetime.now(),
        "description": "adwadwadwa",
    }
    oper.insert_into_table("offers", data)


def check_features(oper):
    additional_data = {
        "two_floors": 1,
        "elevator": 1,
        "balcony": 1,
        "parking_space": 1,
        "storage": 1,
        "cellar": 1,
        "ac": 1,
        "separate_kitchen": 1,
        "garden": 1,

    }

    furnishing_data = {
        "furniture": 0,
        "fridge": 0,
        "oven": 0,
        "stove": 0,
        "washing_machine": 0,
        "dishwasher": 0,
        "tv": 0,
    }

    safety_data = {
        "intercom": 1,
        "monitoring": 0,
        "doors_windows": 1,
        "closed_area": 1,
        "alarm": 0,
        "roller_blinds": 1,
    }

    media_data = {
        "tv": 0,
        "internet": 1,
        "phone": 1}

    test_data = {
        "additional_features": additional_data,
        "safety_features": safety_data,
        "furnishing_features": furnishing_data,
        "media_features": media_data,
    }
    oper.add_offer_features(1, test_data)


def check_add_location(oper):
    loc_data = {
        'address': 'Warszawa, Wola, ul. Marcina Kasprzaka',
        'coordinates': {
            'latitude': 52.2279436,
            'longitude': 20.9586224
        },
        'geo_levels': {
            'city': 'Warszawa',
            'district': 'Wola',
            'subregion': 'Warszawa',
            'region': 'mazowieckie',
        }
    }
    oper.add_location(1, loc_data)


if __name__ == "__main__":
    load_dotenv()

    DB_HOST: str = str(os.getenv("DB_HOST"))
    DB_USER: str = str(os.getenv("DB_USER"))
    DB_PASSWORD: str = str(os.getenv("DB_PASSWORD"))
    DB_NAME: str = str(os.getenv("DB_NAME"))

    db_config: Dict[str, str] = {
        "host": DB_HOST,
        "user": DB_USER,
        "password": DB_PASSWORD,
        'database': DB_NAME
    }

    with SQLInitiator(db_config) as initiator:
        initiator.reset_db()
        initiator.init_all_tables()
        initiator.fill_all_features_tables()
        add_offer(initiator)

    with SQLOperator(db_config) as operator:
        check_add_location(operator)
        check_features(operator)
