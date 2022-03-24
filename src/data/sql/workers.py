import mysql.connector
from mysql.connector.connection import MySQLConnection
from mysql.connector.cursor import MySQLCursor
from itertools import product
from dotenv import load_dotenv
import os

import create_table_queries


# TODO Change add_offer_features to use SELECT WHERE to obtain id of feature set
# TODO figure out a better way to add_offer and add_location. Again using SELECT
#  WHERE
# TODO change SQLWorker to use __del__? Not sure if using context manager is the
#  best way forward


class SQLWorker:

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
        except AttributeError:
            print("Not closable")

    def insert_into_table(self, table, data):
        column_names = self.get_column_names(table)
        column_names_string = ", " .join(column_names)

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

        return tuple(column[0] for column in self.cursor.fetchall()[1:])

    def execute_insert_query(self, query, data=None):   # TODO change name
        try:
            self.cursor.execute(query, data)
            self.db_conn.commit()
        except mysql.connector.Error as err:
            print(err.msg, "ERR_No:", err.errno)

    def execute_read_query(self, query):    # TODO change name
        try:
            self.cursor.execute(query)
        except mysql.connector.Error as err:
            print(err.msg, "ERR_No:", err.errno)


class SQLInitiator(SQLWorker):

    def __init__(self, config):
        super().__init__(config)
        self.tables = {}

    def clear_db(self):
        self.cursor.execute("DROP DATABASE IF EXISTS otodom;")
        self.cursor.execute("CREATE DATABASE otodom;")
        self.cursor.execute("USE otodom;")

    def init_all_tables(self):
        create_table_queries.all_tables(self.tables)        # TODO don't like this maybe move the whole class there
        for table_name in self.tables:
            table_description = self.tables[table_name]
            print(f"Creating table {table_name}: ", end='')
            self.execute_insert_query(table_description)

    def fill_all_features_tables(self):
        feature_tables = ("additional_features", "safety_features",
                          "media_features", "furnishing_features")
        for table in feature_tables:
            column_names = self.get_column_names(table)
            columns_count = len(column_names)

            for combination in product([0, 1], repeat=columns_count):
                data = {column_names[i]: combination[i] for i in range(columns_count)}
                self.insert_into_table(table, data)


# TODO rework to use insert_into_table()
class SQLOperator(SQLWorker):

    def add_images(self, offer_id, images_urls):
        query = ("INSERT INTO images"
                 "(offer_id, image_url)"
                 "VALUES(%s, %s)")
        for url in images_urls:
            data = (offer_id, url)
            self.execute_insert_query(query, data)

    def add_offer(self, data):
        query = ("INSERT INTO offers"
                 "(url, date_created, date_modified, description)"
                 "VALUES (%s, %s, %s, %s)")     # TODO change to a dict?
        self.execute_insert_query(query, data)

    def add_additional_features(self, data):
        query = ("INSERT INTO additional_features"
                 "(two_floors, elevator, balcony, parking_space,"
                 "storage, cellar, ac, separate_kitchen, garden)"
                 "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)")     # TODO change to a dict?
        self.execute_insert_query(query, data)

    def add_safety_features(self, data):
        query = ("INSERT INTO safety_features"
                 "(intercom, monitoring, doors_windows,"
                 " closed_area, alarm, roller_blinds)"
                 "VALUES (%s, %s, %s, %s, %s, %s)")     # TODO change to a dict?
        self.execute_insert_query(query, data)

    def add_media_features(self, data):
        query = ("INSERT INTO media_features"
                 "(tv, internet, phone)"
                 "VALUES (%s, %s, %s)")
        self.execute_insert_query(query, data)

    def add_furnishing_features(self, data):
        query = ("INSERT INTO furnishing_features"
                 "(furniture, fridge, oven, stove,"
                 " washing_machine, dishwasher, tv)"
                 "VALUES (%s, %s, %s, %s, %s, %s, %s)")     # TODO change to a dict?
        self.execute_insert_query(query, data)

    def add_offer_features(self, data):
        query = ("INSERT INTO offer_features"
                 "(additional_id, safety_id, furnishing_id, media_id)"
                 "VALUES (%s, %s, %s, %s)")
        self.execute_insert_query(query, data)

    def add_location(self, data):
        query = ("INSERT INTO locations"
                 "(address, geolevels_id, coordinates_id)"
                 "VALUES (%s, %s, %s)")
        self.execute_insert_query(query, data)

    def add_coordinates(self, data):
        query = ("INSERT INTO coordinates"
                 "(longitude, latitude)"
                 "VALUES(%(longitude)s, %(latitude)s)")
        self.execute_insert_query(query, data)

    def add_geolevel(self, data):
        query = ("INSERT INTO geolevels"
                 "(district, city, subregion, region)"
                 "VALUES(%(district)s, %(city)s, %(subregion)s, %(region)s )")
        self.execute_insert_query(query, data)

    def add_characteristics(self, data):
        query = ("INSERT INTO characteristics"
                 "(price, area, price_per_meter, no_of_rooms, market,"
                 " floor, year_built, no_of_floors, form_of_ownership,"
                 " type_of_building, heating, standard_of_completion,"
                 " type_of_ownership, windows, material, available_from,"
                 " remote_service)"
                 "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,"
                 " %s, %s, %s, %s, %s, %s)")
        self.execute_insert_query(query, data)


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
    with SQLInitiator(db_config) as initiator:
        initiator.clear_db()
        initiator.init_all_tables()
        initiator.fill_all_features_tables()
