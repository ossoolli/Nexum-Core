#!/bin/bash
# Nexum-Core GCP IAM Setup Script
# Sovereign Execution / Jailed Design

set -e

if [ -z "$1" ]; then
    echo "Usage: ./infra/gcp_iam_setup.sh <PROJECT_ID> <SERVICE_ACCOUNT_EMAIL>"
    exit 1
fi

PROJECT_ID=$1
SA_EMAIL=$2

echo "Configuring IAM for Project: $PROJECT_ID, SA: $SA_EMAIL"

# Define Roles
ROLES=(
    "roles/aiplatform.user"
    "roles/discoveryengine.editor"
    "roles/bigquery.dataEditor"
    "roles/bigquery.jobUser"
    "roles/run.admin"
    "roles/run.invoker"
)

# Apply Roles
for ROLE in "${ROLES[@]}"; do
    echo "Assigning $ROLE to $SA_EMAIL..."
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:$SA_EMAIL" \
        --role="$ROLE"
done

echo "IAM configuration completed successfully."
