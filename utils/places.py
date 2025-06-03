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

places_API_key = os.getenv("GOOGLE_PLACES_API_KEY")

def get_place_id(location):
  # Find a place using Text Search
  url = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={location}&inputtype=textquery&fields=place_id&key={places_API_key}"
  response = requests.get(url).json()

  if response['status'] == 'OK':
      place_id = response['candidates'][0]['place_id']

      return place_id
  else:
      print("Error finding place")