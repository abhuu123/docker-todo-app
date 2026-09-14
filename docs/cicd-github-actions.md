# GitHub Actions CI/CD

The GitHub Actions pipeline is designed for a one-click/manual production deployment.

## Flow

1. Developer pushes to `main` or manually starts the workflow.
2. GitHub checks out the repository.
3. Python dependencies are installed.
4. Basic validation/tests run.
5. Docker image is built.
6. Image is tagged with the Git commit SHA.
7. Image is pushed to ECR.
8. GitHub calls AWS SSM.
9. SSM runs `scripts/deploy.sh` on EC2.
10. The deployment script pulls the exact image and runs a health check.

## Authentication

Use GitHub OIDC to assume an AWS IAM role. Do not create long-lived AWS access keys for the repository.

## Required values

In `.github/workflows/deploy.yml`:

```yaml
AWS_REGION: ap-south-1
ECR_REPOSITORY: taskflow
EC2_INSTANCE_ID: i-xxxxxxxxxxxxxxxxx
```

Repository secret:

```text
AWS_DEPLOY_ROLE_ARN
```
