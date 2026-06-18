output "job_id" {
  description = "Patient360 pipeline job ID"
  value       = databricks_job.patient360_pipeline.id
}

output "catalog_name" {
  description = "Unity Catalog name"
  value       = databricks_catalog.patient360.name
}

output "raw_schema" {
  value = databricks_schema.raw.name
}

output "silver_schema" {
  value = databricks_schema.silver.name
}

output "gold_schema" {
  value = databricks_schema.gold.name
}
