# Copyright 2025 Google LLC
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

create_table_query= """
CREATE TABLE `<table_name>`
(
  name STRING NOT NULL OPTIONS(description="name of the event"),
  description STRING OPTIONS(description="event description"),
  location STRING OPTIONS(description="event location"),
  url STRING OPTIONS(description="event url"),
  category STRING OPTIONS(description="event category. e.g. sports, arts, food etc."),
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP() OPTIONS(description="auto-generated timestamp"),
  start_date STRING,
  end_date STRING,
  destination STRING,
  id STRING NOT NULL
);
"""