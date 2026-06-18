#!/bin/bash
# ============================================================
# Patient360 - Workspace Deployment Script
# Uploads all notebooks and SQL files to Databricks Workspace
# Usage: bash workspace/deploy_to_workspace.sh [target]
# target: dev (default) | qa | prod
# ============================================================

set -e

TARGET="${1:-dev}"
WORKSPACE_PATH="/Workspace/patient360"

echo "========================================"
echo " Patient360 Workspace Deployment"
echo " Target: $TARGET"
echo " Workspace: $WORKSPACE_PATH"
echo "========================================"

# Validate auth
echo "[1/7] Validating Databricks auth..."
databricks clusters list > /dev/null && echo "  Auth OK"

# Create workspace directories
echo "[2/7] Creating workspace directories..."
databricks workspace mkdirs "$WORKSPACE_PATH/notebooks/bronze"
databricks workspace mkdirs "$WORKSPACE_PATH/notebooks/silver"
databricks workspace mkdirs "$WORKSPACE_PATH/notebooks/gold"
databricks workspace mkdirs "$WORKSPACE_PATH/notebooks/utils"
databricks workspace mkdirs "$WORKSPACE_PATH/notebooks/validation"
databricks workspace mkdirs "$WORKSPACE_PATH/sql"
databricks workspace mkdirs "$WORKSPACE_PATH/src/ingestion"
databricks workspace mkdirs "$WORKSPACE_PATH/src/bronze"
databricks workspace mkdirs "$WORKSPACE_PATH/src/silver"
databricks workspace mkdirs "$WORKSPACE_PATH/src/gold"

# Upload Bronze notebooks
echo "[3/7] Uploading Bronze notebooks..."
for f in workspace/notebooks/bronze/*.py; do
  fname=$(basename "$f" .py)
  databricks workspace import "$f" "$WORKSPACE_PATH/notebooks/bronze/$fname" --overwrite --language PYTHON
  echo "  Uploaded: $fname"
done

# Upload Silver notebooks
echo "[4/7] Uploading Silver notebooks..."
for f in workspace/notebooks/silver/*.py; do
  fname=$(basename "$f" .py)
  databricks workspace import "$f" "$WORKSPACE_PATH/notebooks/silver/$fname" --overwrite --language PYTHON
  echo "  Uploaded: $fname"
done

# Upload Gold notebooks
echo "[5/7] Uploading Gold notebooks..."
for f in workspace/notebooks/gold/*.py; do
  fname=$(basename "$f" .py)
  databricks workspace import "$f" "$WORKSPACE_PATH/notebooks/gold/$fname" --overwrite --language PYTHON
  echo "  Uploaded: $fname"
done

# Upload utils and validation
echo "[6/7] Uploading utils and validation notebooks..."
for f in workspace/notebooks/utils/*.py workspace/notebooks/validation/*.py; do
  dir=$(dirname "$f" | sed 's|workspace/notebooks/||')
  fname=$(basename "$f" .py)
  databricks workspace import "$f" "$WORKSPACE_PATH/notebooks/$dir/$fname" --overwrite --language PYTHON
  echo "  Uploaded: $dir/$fname"
done

# Upload SQL files
echo "[7/7] Uploading SQL assets..."
for f in workspace/sql/*.sql; do
  fname=$(basename "$f")
  databricks workspace import "$f" "$WORKSPACE_PATH/sql/$fname" --overwrite --language SQL
  echo "  Uploaded: $fname"
done

echo ""
echo "========================================"
echo " Deployment Complete!"
echo " Workspace: $WORKSPACE_PATH"
echo " Browse: https://<workspace>.azuredatabricks.net/browse/folders/patient360"
echo "========================================"
