import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="iski2kxx!",
    database="otodom"
)

db.close()
