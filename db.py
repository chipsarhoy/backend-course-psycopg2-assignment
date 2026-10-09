import psycopg2
import os

database_name = os.environ.get("DATABASE_NAME")
database_user = os.environ.get("DATABASE_USER")
database_password = os.environ.get("DATABASE_PASSWORD")
database_host = os.environ.get("DATABASE_HOST")

conn = psycopg2.connect(f"dbname='{database_name}' user='{database_user}' host='{database_host}' password='{database_password}'")
cursor = conn.cursor()

def create_all():
    print("Creating tables...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Companies (
        company_id SERIAL PRIMARY KEY,
        company_name VARCHAR NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS Products (
        product_id SERIAL PRIMARY KEY,
        company_id INT NOT NULL,  
        product_name VARCHAR NOT NULL UNIQUE,
        description VARCHAR,
        price FLOAT,
        active BOOLEAN DEFAULT True,
        FOREIGN KEY (company_id) REFERENCES Companies(company_id)
        );

        CREATE TABLE IF NOT EXISTS Warranties (
        warranty_id SERIAL PRIMARY KEY,
        product_id INT NOT NULL,
        warranty_months VARCHAR NOT NULL,
        FOREIGN KEY (product_id) REFERENCES Products(product_id)
        );

        CREATE TABLE IF NOT EXISTS Categories (
        category_id SERIAL PRIMARY KEY,
        category_name VARCHAR NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS ProductsCategoriesXref (
        product_id INT REFERENCES Products(product_id),
        category_id INT REFERENCES Categories(category_id),
        PRIMARY KEY (product_id, category_id)
        );
        
    """)

    conn.commit()

