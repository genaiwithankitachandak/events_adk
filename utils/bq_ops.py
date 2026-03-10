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
from utils.places import get_place_id

logging.getLogger().setLevel(logging.INFO)

class BQOps:
    def __init__(self):
        """
        Initializes the BigQuery client to store events data.
        """ 
        self.bq_client = bigquery.Client(project=os.getenv("GOOGLE_CLOUD_PROJECT"))

        # Optional to add it to BQ table for reference run.
        self.run_id = str(uuid.uuid4()).replace('-', '')

    def format_json_for_bq(self, events_json):
        """
        Format json data for BQ table.
        1. Format json and strip extra strings
        2. Add unique ID based on location and event start date and end  date
        3. Use Google places API to get unique id for a location

        Assumption for unique_id : At a given location there will be one event of given category in the given date range.
        """
        events_json = events_json.lstrip("```json")
        events_json = events_json.rstrip("```")
        json_data = json.loads(events_json)
        for event in json_data['events']:
            unique_id = get_place_id(event['location'])
            event['unique_id'] = f"{unique_id}_{event['start_date']}_{event['end_date']}"

        return json_data


    def insert_to_bq(self, json_data, destination_airport_code):
        """
        Insert events data to BQ
        """
        table_id = os.getenv("EVENTS_DATA_TABLE")

        json_data = self.format_json_for_bq(json_data)

        rows_to_insert = []
        for event in json_data["events"]:          
            row = {
                "destination": destination_airport_code,
                "name": event["name"],
                "description": event["description"],
                "start_date": event["start_date"],
                "end_date": event["end_date"],
                "location": event["location"],
                "url": event["url"],
                "category": event["category"],
                "id": event["unique_id"]
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

    def get_events(self, destination=None, start_date=None, end_date=None):
        """
        Retrieve events data from BQ based on optional filters.
        """
        table_id = os.getenv("EVENTS_DATA_TABLE")
        query = f"SELECT * FROM `{table_id}` WHERE 1=1"
        
        query_params = []
        if destination:
            query += " AND destination = @destination"
            query_params.append(bigquery.ScalarQueryParameter("destination", "STRING", destination))
        if start_date:
            # Note: start_date is a STRING in the schema
            query += " AND start_date >= @start_date"
            query_params.append(bigquery.ScalarQueryParameter("start_date", "STRING", start_date))
        if end_date:
            query += " AND end_date <= @end_date"
            query_params.append(bigquery.ScalarQueryParameter("end_date", "STRING", end_date))
            
        job_config = bigquery.QueryJobConfig(query_parameters=query_params)
        
        try:
            query_job = self.bq_client.query(query, job_config=job_config)
            results = query_job.result()
            # Convert QueryResults to dicts and fix timestamp formats
            events = []
            for row in results:
                row_dict = dict(row)
                if 'timestamp' in row_dict and row_dict['timestamp']:
                    row_dict['timestamp'] = row_dict['timestamp'].isoformat()
                events.append(row_dict)
            return events
        except Exception as e:
            logging.error(f"Error querying events: {e}")
            return []