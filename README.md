SpaceONE Repository Service

# Release Notes

## v1.4.1
- Support Private Docker Registry
## v1.4.2
- Support Private GCP Artifact Registry


# Configuration




## Docker Hub Setup ( Docker Hub )
~~~
CONNECTORS:
	DockerHubConnector:
		registry_url:"<registry_url>"

REGISTRY_INFO:
	DOCKER_HUB:
		url: registry.hub.docker.com
DEFAULT_REGISTRY: "DOCKER_HUB"
~~~

## AWS Setup (ECR)
~~~
CONNECTORS:
	AWSPrivateECRConnector:
		aws_access_key_id: "<AWS_ACCESS_KEY_ID>"
		aws_secret_access_key: "<AWS_SECRET_ACCESS_KEY>"
		region_name: "<ap-northeast-2>"
		account_id: "<123456789012>"

REGISTRY_INFO:
	AWS_PRIVATE_ECR:
		url: "<account_id>.dkr.ecr.<region>.amazonaws.com"

DEFAULT_REGISTRY: "AWS_PRIVATE_ECR"
~~~

- Example url: `123456789012.dkr.ecr.ap-northeast-2.amazonaws.com`
- If you set `DEFAULT_REGISTRY` to `AWS_PRIVATE_ECR`, plugin images are pulled from ECR.


## GCP Setup (Artifact Registry)

Prepare a service account key (JSON) and use its Base64-encoded string.

~~~
CONNECTORS:
	GCPPrivateGCRConnector:
		project_id: "<my-project-id>"  # Optional; inferred from the service account key when omitted
		repository_id: "<artifact-registry-repo-id>"
		location: "<artifact-registry-repo-location>"
		service_account_key: "<BASE64_ENCODED_SERVICE_ACCOUNT_JSON>"

REGISTRY_INFO:
	GCP_PRIVATE_GCR:
		url: "<location>-docker.pkg.dev/<project_id>/<repository_id>"

DEFAULT_REGISTRY: "GCP_PRIVATE_GCR"
~~~

- Example url: `asia-northeast3-docker.pkg.dev/my-project/gcr-repository`
- If you set `DEFAULT_REGISTRY` to `GCP_PRIVATE_GCR`, plugin images are pulled from Artifact Registry.
