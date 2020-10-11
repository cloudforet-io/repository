SpaceONE Repository Service

# Release Notes

## v1.4.1
- Support Private Docker Registry


# Configuration

## FOR AWS ECR User

~~~
CONNECTOR:
	RegistryConnector:
		host: https://<account_id>.dkr.ecr.<region_name>.amazonaws.com
		verify_ssl: False
		username: AWS
		api_version: 2
~~~
