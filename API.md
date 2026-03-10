# Events Agent API Documentation

The Events Agent application exposes a RESTful API powered by FastAPI. This API allows you to trigger the event search pipeline and automatically insert the discovered events into Google BigQuery.

## Endpoints

### 1. Trigger Agent Run

Triggers the AI agent to search for events based on the provided parameters and stores the results in BigQuery.

*   **URL:** `/run`
*   **Method:** `POST`
*   **Content-Type:** `application/json`

#### Request Body

The request body is a JSON object with the following fields:

| Field | Type | Required / Optional | Default Value | Description |
| :--- | :--- | :--- | :--- | :--- |
| `destination` | string | Optional | `"SEA"` | The destination city code or name to search for events (e.g., "NYC", "London", "SEA"). |
| `start_date` | string | Optional | `"07/15/2025"` | The start date for the event search in `MM/DD/YYYY` format. |
| `end_date` | string | Optional | `"07/31/2025"` | The end date for the event search in `MM/DD/YYYY` format. |
| `event` | string | Optional | *None* | Specific event name or category to filter by (e.g., "Grand Prix", "Concert"). |

**Example Request Payload:**
```json
{
  "destination": "JFK",
  "start_date": "12/01/2025",
  "end_date": "12/10/2025"
}
```

#### Response

*   **Success Status Code:** `200 OK`
*   **Content-Type:** `application/json`

**Example Response:**
```json
{
  "status": "success",
  "message": "Agent execution and BQ insertion completed."
}
```

### 2. Retrieve Events

Retrieves events that were previously stored in BigQuery. Supports optional filtering.

*   **URL:** `/events`
*   **Method:** `GET`

#### Query Parameters

| Parameter | Type | Required / Optional | Description |
| :--- | :--- | :--- | :--- |
| `destination` | string | Optional | Filter by destination code/name (e.g., "SEA"). |
| `start_date` | string | Optional | Retrieve events starting on or after this date (format: `MM/DD/YYYY` or `YYYY-MM-DD` depending on ingestion). |
| `end_date` | string | Optional | Retrieve events ending on or before this date. |

**Example Request:**
```bash
curl "https://events-agent-service-rucvkjrn2q-uc.a.run.app/events?destination=SEA&start_date=07/15/2025"
```

#### Response

*   **Success Status Code:** `200 OK`
*   **Content-Type:** `application/json`

**Example Response:**
```json
{
  "status": "success",
  "count": 2,
  "events": [
    {
      "name": "Summer Music Festival",
      "description": "Annual music festival.",
      "location": "Seattle Center",
      "url": "https://example.com/fest",
      "category": "Music",
      "timestamp": "2025-07-15T10:00:00Z",
      "start_date": "07/15/2025",
      "end_date": "07/17/2025",
      "destination": "SEA",
      "id": "abc123_07/15/2025_07/17/2025"
    }
  ]
}
```

### 3. Interactive Web UI (ADK)

Because the API is built using the Google Agent Development Kit (ADK) with the `web=True` flag enabled, an interactive web chat interface is also available for debugging and interacting with the agent manually.

*   **URL:** `/` (Root URL)
*   **Method:** `GET`
*   **Description:** Opens the ADK Web UI in your browser. Note: This interface may be disabled in production depending on your deployment configuration.

---

## Interactive API Docs (Swagger UI & ReDoc)

FastAPI automatically generates interactive API documentation. When the application is running (either locally or on Cloud Run), you can access these at:

*   **Swagger UI:** `GET /docs` (Allows you to execute API calls directly from your browser)
*   **ReDoc:** `GET /redoc` (Provides a cleaner, more detailed static view of the API schema)
