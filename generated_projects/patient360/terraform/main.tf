resource "databricks_catalog" "patient360" {
  name    = var.catalog_name
  comment = "Patient360 Analytics Platform - Unity Catalog"
}

resource "databricks_schema" "raw" {
  catalog_name = databricks_catalog.patient360.name
  name         = "patient_360_raw"
  comment      = "Raw ingestion layer"
}

resource "databricks_schema" "bronze" {
  catalog_name = databricks_catalog.patient360.name
  name         = "patient_360_bronze"
  comment      = "Bronze Delta tables"
}

resource "databricks_schema" "silver" {
  catalog_name = databricks_catalog.patient360.name
  name         = "patient_360_silver"
  comment      = "Silver cleansed and standardized layer"
}

resource "databricks_schema" "gold" {
  catalog_name = databricks_catalog.patient360.name
  name         = "patient_360_gold"
  comment      = "Gold analytical datasets and KPIs"
}

resource "databricks_job" "patient360_pipeline" {
  name = "Patient360 Analytics Pipeline - ${var.environment}"

  schedule {
    quartz_cron_expression = "0 0 2 * * ?"
    timezone_id            = "Asia/Kolkata"
    pause_status           = "UNPAUSED"
  }

  email_notifications {
    on_failure = [var.notification_email]
  }

  task {
    task_key = "ingest_source"
    existing_cluster_id = var.cluster_id
    notebook_task {
      notebook_path = "/Workspace/patient360/src/ingestion/ingest_patient_records"
      base_parameters = {
        catalog       = var.catalog_name
        source_schema = var.source_schema
        raw_schema    = "patient_360_raw"
      }
    }
  }

  task {
    task_key = "bronze_load"
    depends_on { task_key = "ingest_source" }
    existing_cluster_id = var.cluster_id
    notebook_task {
      notebook_path = "/Workspace/patient360/src/bronze/bronze_load_all"
      base_parameters = {
        catalog    = var.catalog_name
        raw_schema = "patient_360_raw"
      }
    }
  }

  task {
    task_key = "silver_transform"
    depends_on { task_key = "bronze_load" }
    existing_cluster_id = var.cluster_id
    notebook_task {
      notebook_path = "/Workspace/patient360/src/silver/silver_transform_all"
      base_parameters = {
        catalog       = var.catalog_name
        silver_schema = "patient_360_silver"
      }
    }
  }

  task {
    task_key = "gold_build"
    depends_on { task_key = "silver_transform" }
    existing_cluster_id = var.cluster_id
    notebook_task {
      notebook_path = "/Workspace/patient360/src/gold/gold_build_all"
      base_parameters = {
        catalog       = var.catalog_name
        silver_schema = "patient_360_silver"
        gold_schema   = "patient_360_gold"
      }
    }
  }

  task {
    task_key = "dashboard_refresh"
    depends_on { task_key = "gold_build" }
    existing_cluster_id = var.cluster_id
    notebook_task {
      notebook_path = "/Workspace/patient360/src/gold/refresh_dashboard_datasets"
      base_parameters = {
        catalog     = var.catalog_name
        gold_schema = "patient_360_gold"
      }
    }
  }
}

resource "databricks_grants" "catalog_grants" {
  catalog = databricks_catalog.patient360.name
  grant {
    principal  = "data_engineers"
    privileges = ["USE_CATALOG", "CREATE_SCHEMA", "CREATE_TABLE"]
  }
  grant {
    principal  = "data_analysts"
    privileges = ["USE_CATALOG", "SELECT"]
  }
}
