# Jenkins CI/CD

Jenkins is provided as an alternative to GitHub Actions for organizations that already use Jenkins.

## Flow

```text
GitHub
  ↓
Jenkins
  ↓
Checkout
  ↓
Test
  ↓
Docker Build
  ↓
ECR Push
  ↓
SSM Run Command
  ↓
EC2
  ↓
Docker Compose
  ↓
Health Check
```

The supplied `Jenkinsfile` uses the Jenkins AWS integration (`withAWS`). Configure the Jenkins AWS credential/role with permission to push to ECR and send SSM commands.

For production, use IAM roles or another short-lived credential mechanism where supported rather than storing permanent AWS access keys in Jenkins.
