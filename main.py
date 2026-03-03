import os
import logging
import json
import asyncio
from pydantic import BaseModel
from fastapi import FastAPI
import uvicorn

# Setup logging immediately
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info("Initializing application module...")

try:
    from google.adk.cli.fast_api import get_fast_api_app
    from event_agent.agent import root_agent
    from utils.bq_ops import BQOps
    from utils.agent_session import call_agent
    logger.info("Successfully imported all modules.")
except Exception as e:
    logger.error(f"Import error: {e}", exc_info=True)
    raise

# Lazy initialization for BQOps
_bq_ops = None
def get_bq_ops():
    global _bq_ops
    if _bq_ops is None:
        logger.info("Initializing BigQuery client...")
        _bq_ops = BQOps()
    return _bq_ops

# Create the FastAPI app
try:
    agent_path = os.path.join(os.path.dirname(__file__), "event_agent")
    logger.info(f"Creating FastAPI app with agent_dir: {agent_path}")
    app = get_fast_api_app(agent_dir=agent_path, web=True)
    logger.info("FastAPI app created successfully.")
except Exception as e:
    logger.error(f"Error calling get_fast_api_app: {e}", exc_info=True)
    # Fallback to plain FastAPI if ADK fails, to help with health checks/debugging
    app = FastAPI()

class RunPayload(BaseModel):
    destination: str = "SEA"
    start_date: str = "07/15/2025"
    end_date: str = "07/31/2025"

@app.post("/run")
async def trigger_run(payload: RunPayload):
    """
    Trigger the agent pipeline and BQ insertion via HTTP.
    """
    logging.info(f"Triggering run with payload: {payload}")
    events_json = await call_agent(json.dumps(payload.dict()))
    logging.info("Agent execution completed.")
    
    get_bq_ops().insert_to_bq(events_json, payload.destination)
    return {"status": "success", "message": "Agent execution and BQ insertion completed."}

async def main():
    payload = {
        "destination": "SEA",
        "start_date": "07/15/2025",
        "end_date": "07/31/2025"
    }
    events_json = await call_agent(str(json.dumps(payload)))
    logging.info(events_json)

    get_bq_ops().insert_to_bq(events_json, payload["destination"])

if __name__ == "__main__":
    # Local execution
    logger.info("Running as main script...")
    asyncio.run(main())
