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

from google.adk.sessions import InMemorySessionService
from event_agent.agent import root_agent
from google.adk.runners import Runner
from google.genai import types
import uuid


async def setup_session(USER_ID, SESSION_ID):
    """
    Setup session for agent runner
    """
    session_service = InMemorySessionService()

    # Define constants for identifying the interaction context
    APP_NAME = "events_app"

    # Create the specific session where the conversation will happen
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    print(f"Session created: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'")

    # --- Runner ---
    # Key Concept: Runner orchestrates the agent execution loop.
    runner = Runner(
        agent=root_agent, # The agent we want to run
        app_name=APP_NAME,   # Associates runs with our app
        session_service=session_service # Uses our session manager
    )
    print(f"Runner created for agent '{runner.agent.name}'.")
    return runner, session

async def call_agent(query):
    """
    Helper function to call the agent with a query.
    """
    uid = uuid.uuid4() 
    USER_ID = "user_{uid}"
    SESSION_ID = "session_{uid}"
    runner, session = await setup_session(USER_ID, SESSION_ID)
    content = types.Content(role='user', parts=[types.Part(text=query)])
    events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    for event in events:
        if event.is_final_response():
            if event.author == "url_fetch_agent" and event.content and event.content.parts:
            # For output_schema, the content is the JSON string itself
              print("Author:", event.author)
              final_response = event.content.parts[0].text
            #   print("Agent Response: ", final_response)
              return final_response