import asyncio
import json
from datetime import datetime
from io import BytesIO
import os

import boto3
import polars as pl
from deltalake import DeltaTable
#import s3fs

from libs.repository.database.memory import Memory
from libs.triggers.mellishops import Mellishops
from libs.triggers.vtex import Vtex


class PolarsTooling(object):
    def append_to_lake(self, objects_rows) -> bool:

        object_store = boto3.client(
            "s3",
            aws_access_key_id="lPUW9VLtDxmuFPNWXq4n",
            aws_secret_access_key="iTofnC6nyWdGU1CyxlQzPIBqNKzJzJRcVppjKzC9",
            endpoint_url="http://localhost:9000",
        )

        print(objects_rows[1].trigger_name)

        df = pl.DataFrame(
            {
                "integer": [1, 2, 3],
                "date": [
                    datetime(2025, 1, 1),
                    datetime(2025, 1, 2),
                    datetime(2025, 1, 3),
                ],
                "float": [4.0, 5.0, 6.0],
                "string": ["a", "b", "c"],
            }
        )

        print(df)
        self.write_parquet(object_store, df, "delta-lake", "mellishops.parquet")

        return True

    def write_parquet(self, client, df, bucket, key):
        parquet_io = BytesIO()
        df.write_parquet(parquet_io)

        return client.upload_fileobj(parquet_io, bucket, key)

    def append_to_parquet(file_path: str, new_data: dict):
        """
        Appends new data to an existing Parquet file.
        
        :param file_path: Path to the existing Parquet file.
        :param new_data: Dictionary containing the new data to append.
        """
        try:
            existing_df = pl.read_parquet(file_path)
        except FileNotFoundError:
            existing_df = pl.DataFrame(new_data).head(0)

        new_df = pl.DataFrame(new_data)

        combined_df = pl.concat([existing_df, new_df])

        combined_df.write_parquet(file_path)


    def append_to_deltalake(self, objects_rows) -> bool:

        os.environ["AWS_REGION"] = "local"
        os.environ['AWS_ACCESS_KEY_ID'] = 'lPUW9VLtDxmuFPNWXq4n'
        os.environ['AWS_SECRET_ACCESS_KEY'] = 'iTofnC6nyWdGU1CyxlQzPIBqNKzJzJRcVppjKzC9'
        os.environ['AWS_ENDPOINT_URL'] = 'http://localhost:9000'
        os.environ['AWS_STORAGE_ALLOW_HTTP'] = 'true'
        os.environ['AWS_ALLOW_HTTP'] = 'true'        
        os.environ['AWS_S3_ALLOW_UNSAFE_RENAME'] = 'true'

        print(objects_rows[1].trigger_name)
        
        df2 = pl.DataFrame({
        "name": ["Alice", "Bob", "Charlie"],
        "age": [25, 30, 35],
        "city": ["New York", "Los Angeles", "Chicago"]
        })

        delta_table_path = "s3://deltalakehouse/mellishops"

        df2.write_delta(delta_table_path, mode="append")

        # FOR MORE DOCUMENTATION STUDIES READ:  https://docs.pola.rs/py-polars/html/reference/api/polars.DataFrame.write_delta.html

        return True
