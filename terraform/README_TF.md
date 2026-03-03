# Terraform Deployment Guide

This directory contains Terraform configurations to deploy the Events Agent to Google Cloud Run and set up the necessary BigQuery infrastructure.

## Infrastructure Overview
- **BigQuery Dataset & Table**: Creates the destination for event data with the required schema.
- **Artifact Registry**: A repository to store the agent's Docker image.
- **Cloud Run Service**: Deploys the containerized agent and exposes it via HTTPS.
- **IAM Roles**: Sets up a Service Account with permissions for BigQuery and Vertex AI.

## Prerequisites
1. [Terraform](https://www.terraform.io/downloads.html) installed.
2. [Google Cloud SDK (gcloud)](https://cloud.google.com/sdk/docs/install) installed and authenticated.

## Deployment Steps

### 1. Initialize Terraform
```bash
cd terraform
terraform init
```

### 2. Configure Variables
Copy the example variables file and update it with your project details:
```bash
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your project_id and google_places_api_key
```

### 3. Apply Terraform (Initial Setup)
```bash
terraform apply
```
**Note**: The first run will fail at the Cloud Run step with an "image not found" error. This is expected as we haven't built the container yet. Terraform will still successfully create the Artifact Registry and BigQuery table.

### 4. Build and Push Image using Cloud Build
Run this command from the **root directory** of the project (not the `terraform/` folder):
```bash
# Navigate to root
cd ..

# Build and push to Artifact Registry
# Replace <REGION> and <PROJECT_ID> with your values (e.g., us-central1 and your-project-id)
gcloud builds submit --tag <REGION>-docker.pkg.dev/<PROJECT_ID>/agent-repo/events-agent:latest .
```

### 5. Finalize Cloud Run Deployment
Once the build is successful, return to the `terraform/` folder and run apply again to complete the service deployment:
```bash
cd terraform
terraform apply
```

## Using the Agent
The agent exposes two main ways to interact:
1. **Interactive Demo**: Navigate to the `cloud_run_url` in your browser to use the built-in Google ADK interface.
2. **API Endpoint**: Send a POST request to `<cloud_run_url>/run` to trigger the search and BQ insertion:
```bash
curl -X POST <cloud_run_url>/run \
     -H "Content-Type: application/json" \
     -d '{"destination": "SEA", "start_date": "07/15/2025", "end_date": "07/31/2025"}'
```
