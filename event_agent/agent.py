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

from google.adk.agents import Agent, LlmAgent
from google.adk.tools import google_search
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.sessions import InMemorySessionService
from google.adk.agents import Agent
from google.adk.runners import Runner
from pydantic import BaseModel, Field
from typing import Optional
from google.genai import types
import json
from .prompts import LLM_AGENT_PROMPT


class EventsInput(BaseModel):
    destination: str = Field(description="Event location.")
    start_date: str = Field(description="Event start date in mm/dd/yy format.")
    end_date: str = Field(description="Event end date in mm/dd/yy format.")
    event: Optional[str] = Field(description="Event name.")
    category: Optional[str] = Field(description="Event category.")


class Event(BaseModel):
    name: str = Field(description="Event name.")
    description: str = Field(description="Event description.")
    start_date: str = Field(description="Event start date in mm/dd/yy format.")
    end_date: str = Field(description="Event end date in mm/dd/yy format.")
    location: str = Field(description="Event location.")
    url: str = Field(description="Event URL link. Include ticket links, info links etc.")
    category: str = Field(description="Event category.")

class EventsOutput(BaseModel):
    events : list[Event] = Field(description="List of events.")



events_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="events_agent",
    description="Answers user questions about the current events based on Google grounding.",
    instruction=LLM_AGENT_PROMPT,
    tools=[google_search],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.2 # More deterministic output
    ),
    input_schema=EventsInput,
    output_key="DATA"
)

event_formatter_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="event_formatter_agent",
    description="Answers user questions about the current events based on Google grounding.",
    instruction="""You are an agent that formats events data from DATA and returns output.
      """,
    output_schema=EventsOutput
)

url_fetch_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="url_fetch_agent",
    description="Get url for each event from EventsOutput",
    instruction="You are an agent that get unique_id values for each event and returns respose in same format. Everytime call `map_tool` to get unique_id for the event using key as `formatted_data`.",
    input_schema=EventsOutput)


root_agent = SequentialAgent(
    name="EventPipelineAgent",
    sub_agents=[events_agent, event_formatter_agent, url_fetch_agent]
)