### **Databricks Workspace Deployment Requirement**

After generating all project artifacts, the AI agent MUST deploy every generated asset to the target Databricks workspace for user validation.

#### **Mandatory Deliverables to Databricks Workspace**

The agent shall create and upload:

1. Databricks Notebooks  
   * Bronze notebooks  
   * Silver notebooks  
   * Gold notebooks  
   * Utility notebooks  
   * Validation notebooks  
   * Unit test notebooks  
2. Databricks Jobs  
   * Job definitions  
   * Job workflows  
   * Task dependencies  
   * Scheduled triggers  
3. Delta Live Tables (DLT)  
   * Pipeline definitions  
   * Configuration files  
4. Databricks Dashboards  
   * Executive dashboard  
   * Operational dashboard  
   * Data quality dashboard  
   * Monitoring dashboard  
   * KPI dashboard  
5. Unity Catalog Assets  
   * Catalogs  
   * Schemas  
   * Tables  
   * Views  
6. Databricks Asset Bundle Files  
   * databricks.yml  
   * resources/jobs.yml  
   * resources/pipelines.yml  
   * resources/dashboards.yml  
7. Infrastructure Assets  
   * Terraform files  
   * Environment configurations  
   * Deployment scripts  
8. Documentation  
   * Architecture diagrams  
   * Data flow diagrams  
   * Deployment guides  
   * Runbooks

#### **Deployment Actions**

The agent MUST:

* Authenticate to Databricks Workspace.  
* Create required folders automatically.  
* Upload all generated notebooks.  
* Create jobs and workflows.  
* Create dashboards.  
* Create DLT pipelines.  
* Configure Unity Catalog objects.  
* Validate successful deployment.  
* Generate deployment report.

#### **Verification Requirement**

After deployment, provide:

* Workspace URL  
* Dashboard URLs  
* Job URLs  
* Pipeline URLs  
* Notebook URLs  
* Deployment status report

The user must be able to open Databricks Workspace and visually verify:

* Notebooks  
* Jobs  
* Dashboards  
* Pipelines  
* Catalog objects  
* Documentation

before approving the project.

#### **GitHub Synchronization**

After successful Databricks deployment:

1. Commit all generated files.  
2. Push to GitHub repository.  
3. Create release tag.  
4. Generate deployment manifest.  
5. Store Databricks object IDs and URLs in the repository.

Deployment is considered COMPLETE only when:

* Assets exist in Databricks Workspace.  
* Assets are visible in Databricks UI.  
* Assets are committed to GitHub.  
* Validation report is generated.

