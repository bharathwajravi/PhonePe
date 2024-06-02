import mysql.connector

# Connect to MySQL server
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="charan"
)

# Create database phonepe if it doesn't exist
create_db_query = "CREATE DATABASE IF NOT EXISTS phonepe"
cursor = conn.cursor()
cursor.execute(create_db_query)

# Connect to the phonepe database
conn.database = "phonepe"

# Create table Agg_Trans if it doesn't exist
create_table_query = """
CREATE TABLE IF NOT EXISTS Agg_Trans (
    State VARCHAR(255),
    Year INT,
    Quarter INT,
    Transaction_type VARCHAR(255),
    Transaction_count INT,
    Transaction_amount DECIMAL(30, 10)
)
"""
cursor.execute(create_table_query)

# Create table Agg_User if it doesn't exist
Agg_table_query = """
    CREATE TABLE IF NOT EXISTS Agg_User (
    State VARCHAR(255),
    Year INT,
    Quarter INT,
    RegisteredUsers INT,
    AppOpens BIGINT
)
"""
cursor.execute(Agg_table_query)

# Create table Map_Trans if it doesn't exist
Map_Trans_table_query = """
CREATE TABLE IF NOT EXISTS map_trans (
    State VARCHAR(255),
    District VARCHAR(255),
    Year INT,
    Quarter INT,
    TransactionCount INT,
    TransactionAmount DECIMAL(30, 10)
)
"""
cursor.execute(Map_Trans_table_query)


# Create table Map_User if it doesn't exist
Map_User_table_query = """
CREATE TABLE IF NOT EXISTS Map_User (
    State VARCHAR(255),
    District VARCHAR(255),
    Year INT,
    Quarter INT,
    RegisteredUsers INT,
    AppOpens INT
)
"""
cursor.execute(Map_User_table_query)

# Create table Top_Trans if it doesn't exist
Top_Trans_table_query = """
CREATE TABLE IF NOT EXISTS Top_Trans (
    State VARCHAR(255),
    Entity VARCHAR(255),
    Year INT,
    Quarter INT,
    Transaction_count INT,
    Transaction_amount DECIMAL(30, 10)
)
"""
cursor.execute(Top_Trans_table_query)

# Create table Top_User if it doesn't exist
Top_User_table_query = """
CREATE TABLE IF NOT EXISTS Top_User (
    Category VARCHAR(255),
    Name VARCHAR(255),
    Year INT,
    Quarter INT,
    RegisteredUsers INT
)
"""

cursor.execute(Top_User_table_query)