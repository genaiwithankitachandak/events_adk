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

import os

import uvicorn
from google.adk.cli.fast_api import get_fast_api_app
from utils.bq_ops import BQOps
import json
import asyncio
from utils.agent_session import call_agent
import logging

bq_ops = BQOps()

logging.getLogger().setLevel(logging.INFO)


async def main():
    payload = {
        "destination": "SEA",
        "start_date": "07/15/2025",
        "end_date": "07/31/2025"
    }
    events_json = await call_agent(str(json.dumps(payload)))
    logging.info(events_json)

    bq_ops.insert_to_bq(events_json, payload["destination"])

if __name__ == "__main__":
    asyncio.run(main())
