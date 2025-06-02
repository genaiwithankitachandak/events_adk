## `Copyright 2025 Google LLC`
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import os
import uuid
import logging
from google.cloud import bigquery
from datetime import datetime


logging.getLogger().setLevel(logging.INFO)

class BQOps:
    def __init__(self):
    """
    Initializes the BigQuery client to store events data.
    """
    self.bq_client = bq.Client(project=os.getenv("GOOGLE_CLOUD_PROJECT"))

    # Optional to add it to BQ table for reference run.
    self.run_id = str(uuid.uuid4()).replace('-', '')


    def insert_to_bq(json_data):
        """
        Insert events data to BQ
        """
        table_id = os.getenv("EVENTS_DATA_TABLE")

        rows_to_insert = []
        for event in json_data["events"]:
            # Optional
            # Convert date strings to datetime.date objects
            # BigQuery DATE type expects Python date objects
            start_date_obj = None
            if event["start_date"]:
                try:
                    start_date_obj = datetime.strptime(event["start_date"], "%m/%d/%Y").date()
                except ValueError:
                    logging.Warning(f"Warning: Could not parse start_date '{event['start_date']}' for event '{event['name']}'. Setting to None.")

            end_date_obj = None
            if event["end_date"]:
                try:
                    end_date_obj = datetime.strptime(event["end_date"], "%m/%d/%Y").date()
                except ValueError:
                    logging.Warning(f"Warning: Could not parse end_date '{event['end_date']}' for event '{event['name']}'. Setting to None.")

            # Prepare the row dictionary, ensuring keys match BigQuery column names.
            # if the BQ column is STRING, we convert None to None, and other types to string.
            row = {
                "destination": payload["destination"],
                "name": event["name"],
                "description": event["description"],
                "start_date": event["start_date"],
                "end_date": event["end_date"],
                "location": event["location"],
                "url": event["url"],
                "category": event["category"],
            }
            rows_to_insert.append(row)

        # Insert rows into BigQuery
        logging.info(f"Attempting to insert {len(rows_to_insert)} rows into {table_id}...")
        try:
            # insert_rows_json expects a list of dictionaries, where each dictionary
            # represents a row and its keys match the BigQuery column names.
            errors = self.bq_client.insert_rows_json(table_id, rows_to_insert)

            if errors:
                logging.error("Encountered errors while inserting rows:")
                for error in errors:
                    logging.error(error)
            else:
                logging.info(f"Successfully inserted {len(rows_to_insert)} rows into {table_id}.")
        except Exception as e:
            logging.error(f"An unexpected error occurred during insertion: {e}")