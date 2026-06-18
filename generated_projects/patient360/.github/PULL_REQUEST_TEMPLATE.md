## Summary
<!-- Brief description of what this PR does -->

## Jira Ticket
<!-- Link to Jira ticket: e.g., DV-XX -->

## Type of Change
- [ ] New feature (Bronze/Silver/Gold layer)
- [ ] Bug fix
- [ ] Data quality rule
- [ ] Dashboard update
- [ ] Infrastructure / DAB change
- [ ] Documentation

## Testing
- [ ] Unit tests pass (`pytest tests/ -v`)
- [ ] Coverage >= 80%
- [ ] Tested on DEV Databricks workspace
- [ ] DQ rules validated

## Checklist
- [ ] Code follows PySpark modular standards
- [ ] No hardcoded credentials or catalog paths
- [ ] Unity Catalog references used (catalog.schema.table)
- [ ] Metadata columns present (ingestion_timestamp, record_hash)
- [ ] DQ rejection logic tested
