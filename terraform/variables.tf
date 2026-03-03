variable "project_id" {
  description = "The Google Cloud Project ID"
  type        = string
}

variable "region" {
  description = "The region to deploy the Cloud Run service"
  type        = string
  default     = "us-central1"
}

variable "dataset_id" {
  description = "The BigQuery Dataset ID"
  type        = string
  default     = "events_agent_dataset"
}

variable "table_id" {
  description = "The BigQuery Table ID"
  type        = string
  default     = "events_data"
}

variable "image_name" {
  description = "The name for the container image"
  type        = string
  default     = "events-agent"
}

variable "google_places_api_key" {
  description = "API Key for Google Places API"
  type        = string
  sensitive   = true
}
