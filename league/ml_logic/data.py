import pandas as pd

from google.cloud import bigquery
from league.ml_logic.params import GCP_PROJECT, BQ_DATASET
from pathlib import Path


def get_data_with_cache(query: str, cache_path: Path, data_has_header=True):
    """
    Retrieve `query` data from BigQuery, or from `cache_path` if the file exists
    Store at `cache_path` if retrieved from BigQuery for future use
    """
    if cache_path.is_file():
        df = pd.read_csv(
            cache_path, low_memory=False, header="infer" if data_has_header else None
        )
    else:
        client = bigquery.Client(project=GCP_PROJECT)
        query_job = client.query(query)
        result = query_job.result()
        df = result.to_dataframe()

    if df.shape[0] > 1:
        df.to_csv(cache_path, header=data_has_header, index=False)

    return df


def upload_data_to_bq(data: pd.DataFrame, table: str, truncate: bool):
    """
    - Save the DataFrame to BigQuery
    - Empty the table beforehand if `truncate` is True, append otherwise
    """
    assert isinstance(data, pd.DataFrame)
    full_table_name = f"{GCP_PROJECT}.{BQ_DATASET}.{table}"

    client = bigquery.Client()

    # Define write mode and schema
    write_mode = "WRITE_TRUNCATE" if truncate else "WRITE_APPEND"
    job_config = bigquery.LoadJobConfig(write_disposition=write_mode)

    # Load data
    job = client.load_table_from_dataframe(data, full_table_name, job_config=job_config)
    job.result()
