import datetime

import mysql.connector
from mysql.connector.connection import MySQLConnection
from mysql.connector.cursor import MySQLCursor
from itertools import product
from dotenv import load_dotenv
import os

import tables_create_queries


# TODO change SQLWorker to use __del__? Not sure if using context manager is the best way forward
class SQLWorker:
    # TODO maybe change order of methods
    def __init__(self, config):
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
    def insert_into_table(self, table, data):
        # TODO probably unnecessary but might be needed to check if data is correct
        column_names = self.get_column_names(table)
        column_names_string = ", ".join(column_names)
        values_string = ", ".join(
            (f'%({column_name})s' for column_name in column_names)
        )
        insert_query = (f"INSERT INTO {table} "
                        f"({column_names_string}) "
                        f"VALUES ({values_string})")
        self.execute_insert_query(insert_query, data)

    def get_column_names(self, table):
        column_names_query = ("SELECT column_name "
                              "FROM information_schema.columns "
                              "WHERE table_schema='otodom' "
                              f"AND table_name='{table}'")
        self.execute_read_query(column_names_query)
        column_names = self.get_result_from_cursor()
        return tuple(name for name in column_names if name != "id")

    def get_row_id(self, table, data):
        where_string = " AND ".join([f"{key}=%({key})s" for key in data.keys()])
        get_table_id_query = (f"SELECT EXISTS("
                              f"SELECT id FROM {table} "
                              f"WHERE {where_string})")
        self.execute_read_query(get_table_id_query, data)
        return self.get_result_from_cursor()[0]

    def execute_insert_query(self, query, data=None):
        try:
            self.cursor.execute(query, data)
        except mysql.connector.Error as err:
            print("Invalid insert query")
            print(err.msg, "ERR_No:", err.errno)
        else:
            self.db_conn.commit()

    def execute_read_query(self, query, data=None):
        try:
            self.cursor.execute(query, data)
        except mysql.connector.Error as err:
            print("Invalid read query")
            print(err.msg, "ERR_No:", err.errno)

    def execute_create_table_query(self, query, table_name):
        try:
            print(f"Creating table {table_name}: ", end="")
            self.cursor.execute(query)
        except mysql.connector.Error as err:
            print(f"FAILED, {err.msg}, ERR_No:{err.errno}")
        else:
            print("OK")
            self.db_conn.commit()

    def get_result_from_cursor(self):
        return next(zip(*self.cursor.fetchall()))


class SQLInitiator(SQLWorker):

    def __init__(self, config):
        super().__init__(config)
        self.tables = tables_create_queries.get_all_tables_queries()

    def clear_db(self):
        self.cursor.execute("DROP DATABASE IF EXISTS otodom;")
        self.cursor.execute("CREATE DATABASE otodom;")
        self.cursor.execute("USE otodom;")

    def init_all_tables(self):
        for table_name in self.tables:
            table_description = self.tables[table_name]
            self.execute_create_table_query(table_description, table_name)

        self.fill_all_features_tables()

    def fill_all_features_tables(self):
        feature_tables = ("additional_features", "safety_features",
                          "media_features", "furnishing_features")
        for table in feature_tables:
            column_names = self.get_column_names(table)
            columns_count = len(column_names)

            for combination in product([0, 1], repeat=columns_count):
                data = {column_names[i]: combination[i] for i in range(columns_count)}
                self.insert_into_table(table, data)


class SQLOperator(SQLWorker):

    # TODO it doesn't seem right that those inserts have different methods
    def add_offer_features(self, offer_id, query_data):
        insert_data = {"offer_id": offer_id}
        for key in query_data.keys():
            column_name = key.replace("features", "id")
            insert_data[column_name] = self.get_row_id(key, query_data[key])

        self.insert_into_table("offer_features", insert_data)
    
    def add_location(self, offer_id, data):
        # TODO perhaps split func into coordinates/geo_levels/locations
        data["coordinates"]["offer_id"] = offer_id
        self.insert_into_table("coordinates", data["coordinates"])
        geo_levels_id = self.get_row_id("geo_levels", data)
        if geo_levels_id == 0:
            self.insert_into_table("geo_levels", data)
            geo_levels_id = self.get_row_id("geo_levels", data)

        insert_data = {
            "offer_id": offer_id,
            "address": data["address"],
            "geo_levels_id": geo_levels_id
        }
        self.insert_into_table("locations", insert_data)


if __name__ == "__main__":
    load_dotenv()

    DB_HOST = os.getenv("DB_HOST")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")

    db_config = {
        "host": DB_HOST,
        "user": DB_USER,
        "password": DB_PASSWORD,
        'database': DB_NAME
    }


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


    def check_get_geo_levels_id(oper):
        geo_data = {
            "district": "wola",
            "city": "warszawa",
            "subregion": "warszawa",
            "region": "mazowieckie",
        }
        oper.get_geo_levels_id(geo_data)


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


    with SQLInitiator(db_config) as initiator:
        initiator.clear_db()
        initiator.init_all_tables()
        initiator.fill_all_features_tables()
        add_offer(initiator)

    with SQLOperator(db_config) as operator:
        check_add_location(operator)
        check_get_geo_levels_id(operator)
        check_features(operator)
