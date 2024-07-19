import pandas as pd
import numpy as np
from faker import Faker
import os

# Initialize Faker for generating random data
fake = Faker()

# Configuration
num_rows = 3_000_000  # Number of rows to generate (adjust to get desired file size)
file_path = 'large_file.csv'
chunk_size = 100_000   # Number of rows per chunk to write

# Create a function to generate a chunk of data
def generate_data_chunk(num_rows):
    data = {
        'column1': [fake.text(max_nb_chars=20) for _ in range(num_rows)],
        'column2': np.random.randint(1, 100, size=num_rows),
        'column3': np.random.rand(num_rows) * 100,
        'column4': [fake.date_this_century() for _ in range(num_rows)]
    }
    return pd.DataFrame(data)

# Write data to CSV in chunks
with open(file_path, 'w') as file:
    header = True
    for _ in range(num_rows // chunk_size):
        chunk = generate_data_chunk(chunk_size)
        chunk.to_csv(file, header=header, index=False)
        header = False

# Handle remaining rows if num_rows is not a multiple of chunk_size
remaining_rows = num_rows % chunk_size
if remaining_rows > 0:
    chunk = generate_data_chunk(remaining_rows)
    chunk.to_csv(file_path, mode='a', header=False, index=False)

# Print file size
file_size = os.path.getsize(file_path) / (1024 * 1024 * 1024)
print(f"Generated CSV file size: {file_size:.2f} GB")
