output "cloud_run_url" {
  description = "The URL of the deployed Cloud Run service"
  value       = google_cloud_run_v2_service.events_agent_service.uri
}

output "bq_table_id" {
  description = "The BigQuery table ID"
  value       = "${google_bigquery_table.events_table.project}.${google_bigquery_table.events_table.dataset_id}.${google_bigquery_table.events_table.table_id}"
}

output "artifact_registry_repo" {
  description = "Artifact Registry Repository URL"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.agent_repo.repository_id}/"
}
