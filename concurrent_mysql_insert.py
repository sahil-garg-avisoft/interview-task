import pandas as pd
import mysql.connector
from mysql.connector import Error
import concurrent.futures
import time
from tqdm import tqdm
from dotenv import load_dotenv
import os

load_dotenv()
# Database connection configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'auth_plugin': 'mysql_native_password'
}

# Table creation SQL
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS large_table (
    id INT AUTO_INCREMENT PRIMARY KEY,
    column1 VARCHAR(255),
    column2 INT,
    column3 FLOAT,
    column4 DATE
)
"""

# Insert SQL
INSERT_SQL = """
INSERT INTO large_table (column1, column2, column3, column4)
VALUES (%s, %s, %s, %s)
"""

def create_connection():
    """Create and return a database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
        return None

def create_table(connection):
    """Create the table if it doesn't exist"""
    try:
        cursor = connection.cursor()
        cursor.execute(CREATE_TABLE_SQL)
        connection.commit()
    except Error as e:
        print(f"Error creating table: {e}")

def check_buffer_pool_size(connection):
    """Check and print the current innodb_buffer_pool_size"""
    cursor = connection.cursor()
    cursor.execute("SHOW VARIABLES LIKE 'innodb_buffer_pool_size'")
    result = cursor.fetchone()
    print(f"Current innodb_buffer_pool_size: {int(result[1]) / (1024 * 1024 * 1024):.2f} GB")

def optimize_for_bulk_insert(connection):
    """Apply InnoDB optimizations for bulk insert"""
    cursor = connection.cursor()
    cursor.execute("SET autocommit = 0")
    cursor.execute("SET unique_checks = 0")
    cursor.execute("SET foreign_key_checks = 0")
    # Be cautious with this next setting in production environments
    cursor.execute("SET GLOBAL innodb_flush_log_at_trx_commit = 2")
    connection.commit()
    print("Applied InnoDB optimizations for bulk insert")

def restore_settings(connection):
    """Restore InnoDB settings after bulk insert"""
    cursor = connection.cursor()
    cursor.execute("SET unique_checks = 1")
    cursor.execute("SET foreign_key_checks = 1")
    cursor.execute("SET GLOBAL innodb_flush_log_at_trx_commit = 1")
    connection.commit()
    print("Restored InnoDB settings")

def insert_chunk(chunk):
    """Insert a chunk of data into the database"""
    connection = create_connection()
    if connection is None:
        return
    
    try:
        cursor = connection.cursor()
        data = [tuple(row) for _, row in chunk.iterrows()]
        cursor.executemany(INSERT_SQL, data)
        connection.commit()
    except Error as e:
        print(f"Error inserting data: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def main():
    csv_file = 'large_file.csv'  # Path to your large CSV file
    chunk_size = 10000  # Number of rows per chunk
    max_workers = 30  # Number of concurrent threads (adjust based on performance)

    start_time = time.time()

    # Create the table and apply optimizations
    connection = create_connection()
    if connection is None:
        return

    create_table(connection)
    check_buffer_pool_size(connection)
    optimize_for_bulk_insert(connection)

    # Read and insert data in chunks
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Create an iterable of chunks from the CSV file
        chunks = pd.read_csv(csv_file, chunksize=chunk_size)
        futures = []

        # Submit tasks for each chunk
        for chunk in chunks:
            future = executor.submit(insert_chunk, chunk)
            futures.append(future)

        # Show progress
        for _ in tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="Inserting chunks"):
            pass

    # Restore settings and close connection
    restore_settings(connection)
    connection.close()

    end_time = time.time()
    print(f"Total execution time: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()
