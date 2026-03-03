provider "google" {
  project = var.project_id
  region  = var.region
}

# --- Services ---
resource "google_project_service" "apis" {
  for_each = toset([
    "run.googleapis.com",
    "bigquery.googleapis.com",
    "artifactregistry.googleapis.com",
    "aiplatform.googleapis.com"
  ])
  service            = each.key
  disable_on_destroy = false
}

# --- BigQuery ---
resource "google_bigquery_dataset" "events_dataset" {
  dataset_id = var.dataset_id
  location   = var.region
  depends_on = [google_project_service.apis]
}

resource "google_bigquery_table" "events_table" {
  dataset_id = google_bigquery_dataset.events_dataset.dataset_id
  table_id   = var.table_id

  schema = <<EOF
[
  { "name": "name", "type": "STRING", "mode": "REQUIRED" },
  { "name": "description", "type": "STRING", "mode": "NULLABLE" },
  { "name": "location", "type": "STRING", "mode": "NULLABLE" },
  { "name": "url", "type": "STRING", "mode": "NULLABLE" },
  { "name": "category", "type": "STRING", "mode": "NULLABLE" },
  { "name": "timestamp", "type": "TIMESTAMP", "mode": "NULLABLE", "defaultValueExpression": "CURRENT_TIMESTAMP()" },
  { "name": "start_date", "type": "STRING", "mode": "NULLABLE" },
  { "name": "end_date", "type": "STRING", "mode": "NULLABLE" },
  { "name": "destination", "type": "STRING", "mode": "NULLABLE" },
  { "name": "id", "type": "STRING", "mode": "REQUIRED" }
]
EOF
}

# --- Artifact Registry ---
resource "google_artifact_registry_repository" "agent_repo" {
  location      = var.region
  repository_id = "agent-repo"
  format        = "DOCKER"
  depends_on    = [google_project_service.apis]
}

# --- Service Account ---
resource "google_service_account" "agent_sa" {
  account_id   = "events-agent-sa"
  display_name = "Service Account for Events Agent on Cloud Run"
}

resource "google_project_iam_member" "bq_editor" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.agent_sa.email}"
}

resource "google_project_iam_member" "bq_job_user" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.agent_sa.email}"
}

resource "google_project_iam_member" "aiplatform_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.agent_sa.email}"
}

# --- Cloud Run ---
resource "google_cloud_run_v2_service" "events_agent_service" {
  name     = "events-agent-service"
  location = var.region
  deletion_protection = false

  template {
    service_account = google_service_account.agent_sa.email
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.agent_repo.repository_id}/${var.image_name}:latest"
      
      env {
        name  = "GOOGLE_CLOUD_PROJECT"
        value = var.project_id
      }
      env {
        name  = "GOOGLE_CLOUD_LOCATION"
        value = var.region
      }
      env {
        name  = "EVENTS_DATA_TABLE"
        value = "${var.project_id}.${var.dataset_id}.${var.table_id}"
      }
      env {
        name  = "GOOGLE_PLACES_API_KEY"
        value = var.google_places_api_key
      }
      env {
        name  = "GOOGLE_GENAI_USE_VERTEXAI"
        value = "TRUE"
      }

      ports {
        container_port = 8080
      }
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  depends_on = [google_project_service.apis]
}

# --- IAM for Public Access (Optional, usually better protected but for demo/agent testing) ---
resource "google_cloud_run_v2_service_iam_member" "public_access" {
  name     = google_cloud_run_v2_service.events_agent_service.name
  location = google_cloud_run_v2_service.events_agent_service.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}
