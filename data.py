# data.py
import os
import logging
import dask.dataframe as dd

# Load dataset
current_directory = os.path.dirname(__file__)
csv_file_path = os.path.join(current_directory, 'dataset', 'us_accidents_clean.csv')

# Load dataset using Dask
def load_data(file_path):
    logging.info("Loading data using Dask...")
    try:
        ddf = dd.read_csv(file_path)
        df = ddf.compute()
        if df.empty:
            raise ValueError("The CSV file is empty")
        logging.info("Data loaded successfully using Dask.")
        return df
    except Exception as e:
        logging.error(f"Error loading CSV file: {e}")
        raise RuntimeError(f"Error loading CSV file: {e}")
    
df = load_data(csv_file_path)
if df is None:
    raise ValueError("data.py : DataFrame is not loaded.")