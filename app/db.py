import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="#Vimal2004",
        database="smart_water"
    )
