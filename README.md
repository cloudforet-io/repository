SpaceONE Repository Service

# Release Notes

## v1.4.1
- Support Private Docker Registry
## v1.4.2
- Support Private GCP Artifact Registry


# Configuration

## FOR AWS ECR User

~~~
CONNECTOR:
	RegistryConnector:
		host: https://<account_id>.dkr.ecr.<region_name>.amazonaws.com
		verify_ssl: False
		username: AWS
		api_version: 2

## GCP artifact repository added
CONNECTOR:
	RegistryConnector:
		host: https://<account_id>.dkr.ecr.<region_name>.amazonaws.com
		verify_ssl: False
		username: AWS
		api_version: 2
	GCPPrivateGCRConnector:
		project_id: project id
      	repository_id: gcp's artifact registry id
      	location: 
      	service_account_key: service account key base64 encode 

REGISTRY_INFO:
	GCP_PRIVATE_GCR:
		url: <location>-docker.pkg.dev/<project_id>/<repository_id>
~~~
