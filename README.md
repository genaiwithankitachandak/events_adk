# **Events Agent**

This repository contains the code for an Events Agent, designed to provide information about events happening around the world. It leverages Google ADK (Agent Development Kit) for agent orchestration, google\_search for data grounding, and BigQuery for data storage.

## **Features**

* **Event Information Retrieval**: Uses google\_search to find current events based on user queries (destination, dates, event name, category).  
* **Categorized Event Data**: Covers a wide range of event categories including Arts & Culture, Food & Drink, Sports, Community & Local, Seasonal & Holiday, Business & Professional, Academic & Educational, Health & Wellness, and Hobbies & Special Interests.  
* **Structured Output**: Formats event data into a standardized JSON structure including event name, description, dates, location, URL, and category.  
* **BigQuery Integration**: Inserts retrieved event data into a BigQuery table for persistence and further analysis.  
* **Google ADK Powered**: Built with Google ADK for robust agent development and management.

## **Architecture Diagram**

<img src="misc/agent_architecture.png" alt="Event Multi-Agent Architecture" width="800"/>

### Component Details
<img src="misc/events_architecture.png" alt="Event Multi-Agent Architecture" width="800"/>

## **Setup and Installation**

### **Prerequisites**

Before you begin, ensure you have the following:

* A Google Cloud Project.  
* BigQuery API enabled in your Google Cloud Project.  
* Authentication configured for your Google Cloud environment (e.g., gcloud auth application-default login).  
* Python 3.8+ installed.

### **Project Setup**

1. Copy .env.example file as .env 

    Set your Google Cloud Project ID and Location:  
   Update the PROJECT\_ID and LOCATION variables in the .env file:  
   PROJECT\_ID \= "Project_id"  \# Replace with your GCP Project ID  
   LOCATION \= "us-central1" \# Replace with your preferred GCP region

2. BigQuery Table Configuration:  
   Ensure you have a BigQuery dataset and table created for storing event data. Update the table\_id variable in the in .env with your BigQuery table path:  
   \# Example: table\_id \= "your-gcp-project-id.your\_bigquery\_dataset.events\_agent"  

   The table schema should be compatible with the Event output schema, including columns for destination, name, description, start\_date, end\_date, location, url, and category.

3. Update the places API key in .env. We use Places env to create unique_id for eah event based on location, start_date and end_date

### **Installing Libraries**

Install the necessary Python libraries using pip:

`pip install -r requirements.txt`

### **Running Locally**

```bash
python main.py
```

`main.py` runs the code in the following order:
* Creates a session for the agent.
* Initializes the agent runner with `root_agent`.
* Executes the sequential pipeline and returns results as JSON.
* Generates unique IDs using the Google Places API.
* Inserts the results into your BigQuery table.

## **Cloud Deployment (Google Cloud Run)**

The agent is designed for easy deployment to Google Cloud Run using Terraform.

### **Deployment Steps**
Detailed deployment instructions can be found in [terraform/README_TF.md](terraform/README_TF.md). 

Summary:
1. **Infrastructure Setup**: Use Terraform to create the BigQuery table, Artifact Registry, and Cloud Run service.
2. **Build Image**: Use Google Cloud Build to build the container and push it to the registry.
3. **Deploy**: Re-run `terraform apply` to point the Cloud Run service to your new image.

### **Triggering the Agent (API)**
Once deployed, you can trigger a run by sending a POST request to the `/run` endpoint of your Cloud Run service.

**Example Curl Command:**
```bash
curl -X POST https://events-agent-service-rucvkjrn2q-uc.a.run.app/run \
     -H "Content-Type: application/json" \
     -d '{
       "destination": "SEA",
       "start_date": "07/15/2025",
       "end_date": "07/31/2025"
     }'
```

This will trigger the agent search and automatically insert the found events into BigQuery.

## **Continuous Integration & Deployment (CI/CD)**

This repository includes a GitHub Action in `.github/workflows/deploy.yml` that automatically builds and deploys your agent to Cloud Run whenever you push to the `main` branch.

### **GitHub Secrets Setup**
To enable this, you must add the following **Secrets** to your GitHub Repository settings (`Settings > Secrets and variables > Actions`):

1.  **`GCP_PROJECT_ID`**: Your Google Cloud Project ID (e.g., `experiments-435323`).
2.  **`GCP_SA_KEY`**: The JSON key for a Service Account with permissions to use Cloud Build, Artifact Registry, and Cloud Run.

> **Tip**: You can use the same Service Account created by Terraform (`events-agent-sa`), but you will need to generate and download a JSON key for it from the GCP Console.

## **Agent Details**

The system consists of a sequential agent pipeline:

1. **events\_agent**:  
   * **Model**: gemini-2.0-flash  
   * **Description**: Identifies event locations, uses google\_search to find events across various categories, and extracts detailed event information.  
   * **Tools**: google\_search  
   * **Input Schema**: EventsInput (destination, start\_date, end\_date, event, category)  
   * **Output Key**: DATA  
2. **event\_formatter\_agent**:  
   * **Model**: gemini-2.0-flash  
   * **Description**: Formats the raw event data (DATA) into a structured EventsOutput schema.  
   * **Output Schema**: EventsOutput (list of Event objects)  
   * **Output Key**: formatted\_data  
3. **url\_fetch\_agent**:  
   * **Model**: gemini-2.0-flash  
   * **Description**: This agent's primary role is to process the formatted\_data (though its current implementation with map\_tool returns the input as is, it's set up to potentially fetch unique IDs or additional details for each event).  
   * **Tools**: map\_tool (a custom tool for potential future use with a mapping service).  
   * **Input Schema**: EventsOutput  
4. **event\_pipeline\_agent**:  
   * **Type**: Sequential Agent  
   * **Sub-agents**: events\_agent, event\_formatter\_agent, url\_fetch\_agent  
   * **Functionality**: Orchestrates the flow of data through the individual agents.

## **BigQuery Integration**

The insert\_to\_bq function handles inserting the processed event data into your specified BigQuery table. It converts date strings to datetime.date objects suitable for BigQuery's DATE type.

## **How it Works**
The agent uses a combination of Search Grounding and LLMs to find events. Once found, it validates the locations, fetches unique IDs via the Google Places API, and performs a batch insertion into BigQuery.

## **License**

This project is licensed under the Apache License, Version 2.0 \- see the LICENSE file for details.

Copyright 2025 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");  
you may not use this file except in compliance with the License.  
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software  
distributed under the License is distributed on an "AS IS" BASIS,  
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  
See the License for the specific language governing permissions and  
limitations under the License.  
