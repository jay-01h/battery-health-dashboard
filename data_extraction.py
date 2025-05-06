import pandas as pd
import zipfile
import requests
import os
from io import BytesIO, StringIO

def clean_raw_data(file_path_or_url):
    # Step 1: Load the file (local or URL)
    if file_path_or_url.startswith("http://") or file_path_or_url.startswith("https://"):
        response = requests.get(file_path_or_url)
        if response.status_code != 200:
            raise Exception("Failed to download file.")
        file_data = BytesIO(response.content)
    else:
        file_data = file_path_or_url  # Local path

    # Step 2: Extract and read data from zip
    if (isinstance(file_data, BytesIO) and zipfile.is_zipfile(file_data)) or str(file_data).endswith(".zip"):
        with zipfile.ZipFile(file_data) as z:
            for name in z.namelist():
                if name.endswith(('.csv', '.xlsx', '.xls', '.json')):
                    with z.open(name) as f:
                        file_ext = os.path.splitext(name)[1]
                        df = _read_file_by_type(f, file_ext)
                        break
            else:
                raise ValueError("No valid data file found in zip.")
    else:
        # Handle direct CSV, Excel, or JSON
        file_ext = os.path.splitext(str(file_path_or_url))[1]
        df = _read_file_by_type(file_data, file_ext)

    return _transform_dataframe(df)

# --- Helper: File reader ---
def _read_file_by_type(file_obj, extension):
    if extension == '.csv':
        return pd.read_csv(file_obj)
    elif extension in ('.xlsx', '.xls'):
        return pd.read_excel(file_obj)
    elif extension == '.json':
        return pd.read_json(file_obj)
    else:
        raise ValueError(f"Unsupported file type: {extension}")

# --- Helper: Data transformation ---
def _transform_dataframe(df):
    print("Original Columns:", df.columns.tolist())

    # Rename timestamp column
    for col in df.columns:
        if 'time' in col.lower():
            df.rename(columns={col: 'timestamp'}, inplace=True)
            break

    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        df.dropna(subset=['timestamp'], inplace=True)
    else:
        raise ValueError("Timestamp column not found.")

    # Clean and normalize
    df.dropna(axis=1, how='all', inplace=True)
    df.drop_duplicates(inplace=True)
    numeric_cols = df.select_dtypes(include='number').columns
    df.dropna(subset=numeric_cols, inplace=True)
    df.columns = [col.strip().replace(' ', '_') for col in df.columns]

    print("Cleaned Columns:", df.columns.tolist())
    print("Final Shape:", df.shape)
    return df
