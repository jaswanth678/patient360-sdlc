variable "databricks_host" {
  description = "Databricks workspace URL"
  type        = string
}

variable "databricks_token" {
  description = "Databricks personal access token"
  type        = string
  sensitive   = true
}

variable "cluster_id" {
  description = "Existing cluster ID for running jobs"
  type        = string
}

variable "catalog_name" {
  description = "Unity Catalog name"
  type        = string
  default     = "sdlc_catalog"
}

variable "source_schema" {
  description = "Source schema name"
  type        = string
  default     = "patient_360"
}

variable "notification_email" {
  description = "Email for job notifications"
  type        = string
  default     = ""
}

variable "environment" {
  description = "Deployment environment (dev/qa/prod)"
  type        = string
  default     = "dev"
}
