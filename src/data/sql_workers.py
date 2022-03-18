import mysql.connector
from dotenv import load_dotenv
import os


class SQLWorker:

    def __init__(self, config):
        self.config = config
        self.db_conn = None
        self.cursor = None

    def __enter__(self):
        self.db_conn = mysql.connector.connect(**self.config)
        self.cursor = self.db_conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.cursor.close()
            self.db_conn.close()
        except AttributeError:
            print("Not closable")
            return True

    def add_images(self, offer_id, images_urls):
        query = ("INSERT INTO images"
                 "(offer_id, image_url)"
                 "VALUES(%s, %s)")
        for url in images_urls:
            data = (offer_id, url)
            self.execute_query(query, data)

    def add_offer(self, data):
        query = ("INSERT INTO offers"
                 "(url, date_created, date_modified, description, features_id,"
                 "location_id, characteristics_id)"
                 "VALUES (%s, %s, %s, %s, %s, %s, %s)")     # TODO change to a dict?
        self.execute_query(query, data)

    def add_additional_features(self, data):
        query = ("INSERT INTO additional_features"
                 "(two_floors, elevator, balcony, parking_space,"
                 "storage, cellar, ac, separate_kitchen, garden)"
                 "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)")     # TODO change to a dict?
        self.execute_query(query, data)

    def add_safety_features(self, data):
        query = ("INSERT INTO safety_features"
                 "(intercom, monitoring, doors_windows,"
                 " closed_area, alarm, roller_blinds)"
                 "VALUES (%s, %s, %s, %s, %s, %s)")     # TODO change to a dict?
        self.execute_query(query, data)

    def add_media_features(self, data):
        query = ("INSERT INTO media_features"
                 "(tv, internet, phone)"
                 "VALUES (%s, %s, %s)")
        self.execute_query(query, data)

    def add_furnishing_features(self, data):
        query = ("INSERT INTO furnishing_features"
                 "(furniture, fridge, oven, stove,"
                 " washing_machine, dishwasher, tv)"
                 "VALUES (%s, %s, %s, %s, %s, %s, %s)")     # TODO change to a dict?
        self.execute_query(query, data)

    def add_offer_features(self, data):
        query = ("INSERT INTO offer_features"
                 "(additional_id, safety_id, furnishing_id, media_id)"
                 "VALUES (%s, %s, %s, %s)")
        self.execute_query(query, data)

    def add_location(self, data):
        query = ("INSERT INTO locations"
                 "(address, district_id, coordinates_id)"
                 "VALUES (%s, %s, %s)")
        self.execute_query(query, data)

    def add_coordinates(self, data):
        query = ("INSERT INTO coordinates"
                 "(longitude, latitude)"
                 "VALUES(%(longitude)s, %(latitude)s)")
        self.execute_query(query, data)

    def add_district(self, data):
        query = ("INSERT INTO districts"
                 "(city_id, name)"
                 "VALUES (%s, %s)")
        self.execute_query(query, data)

    def add_cities(self, data):
        query = ("INSERT INTO cities"
                 "(subregion_id, name)"
                 "VALUES (%s, %s)")
        self.execute_query(query, data)

    def add_subregion(self, data):
        query = ("INSERT INTO subregions"
                 "(region_id, name)"
                 "VALUES (%s, %s)")
        self.execute_query(query, data)

    def add_region(self, data):
        query = ("INSERT INTO regions"
                 "(name)"
                 "VALUES (%s)")
        self.execute_query(query, data)

    def add_characteristics(self, data):
        query = ("INSERT INTO characteristics"
                 "(price, area, price_per_meter, no_of_rooms, market,"
                 " floor, year_built, no_of_floors, form_of_ownership,"
                 " type_of_building, heating, standard_of_completion,"
                 " type_of_ownership, windows, material, available_from,"
                 " remote_service)"
                 "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,"
                 " %s, %s, %s, %s, %s, %s)")
        self.execute_query(query, data)

    def execute_query(self, query, data=None):
        try:
            self.cursor.execute(query, data)
            self.db_conn.commit()
            return True
        except mysql.connector.Error as err:
            print(err.errno, err.msg)
            return False


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
