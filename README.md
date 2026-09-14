# TaskFlow — Production Docker Deployment on AWS

TaskFlow is a small Python/FastAPI task-management application created as a **DevOps portfolio project**. The application is intentionally simple so the infrastructure and deployment workflow are easy to understand.

The project demonstrates how to take an application from source code to a production-style Docker deployment using **Docker, Docker Compose, Nginx, PostgreSQL, AWS EC2, Amazon ECR, GitHub Actions or Jenkins, and AWS Systems Manager (SSM)**.

> This is a personal portfolio project. Do not claim it was deployed for a client unless it actually was.

## 1. Architecture

```text
Developer
   │
   ▼
GitHub Repository
   │
   ├───────────────┐
   ▼               ▼
GitHub Actions   Jenkins
   │               │
   └───────┬───────┘
           ▼
       Test + Build
           │
           ▼
       Docker Image
           │
           ▼
        Amazon ECR
           │
           ▼
       AWS SSM
           │
           ▼
        AWS EC2
           │
       Docker Compose
       ┌────┼─────────┐
       ▼    ▼         ▼
    Nginx  FastAPI  PostgreSQL
       │
      HTTPS
       │
       ▼
     Users
```

A standalone architecture diagram is included at `docs/architecture-diagram.png`.

## 2. What the application does

TaskFlow provides a small dashboard where a user can:

- Create tasks
- View tasks
- Mark tasks complete
- Delete tasks
- See task counts

The UI is intentionally polished so the project can also be shown in an Upwork portfolio screenshot.

## 3. Technology stack

- Python 3.12
- FastAPI
- SQLAlchemy
- PostgreSQL 16
- Docker
- Docker Compose
- Nginx
- AWS EC2
- Amazon ECR
- AWS Systems Manager
- GitHub Actions
- Jenkins
- HTTPS/Let's Encrypt

## 4. Prerequisites

### For local development

Install:

- Docker Engine
- Docker Compose v2
- Git

Verify:

```bash
docker --version
docker compose version
git --version
```

You do **not** need Python installed on the host to run the application with Docker.

### For AWS deployment

You need:

- AWS account
- AWS region, e.g. `ap-south-1`
- EC2 instance running a Linux distribution
- Docker + Docker Compose installed on EC2
- AWS CLI installed on EC2
- SSM Agent and an EC2 IAM role that permits SSM and ECR image pulls
- ECR repository named `taskflow`
- Route 53 DNS record if using a domain
- TLS certificate/Let's Encrypt if using HTTPS
- GitHub repository
- Either GitHub Actions with AWS OIDC or Jenkins with AWS credentials/plugin configuration

For a real production environment, prefer SSM instead of public SSH and use short-lived/OIDC credentials instead of static AWS access keys.

## 5. Exact `.env` for local development

The repository includes a working `.env` for the local Docker demo. Its exact contents are:

```env
POSTGRES_DB=taskflow
POSTGRES_USER=taskflow
POSTGRES_PASSWORD=taskflow_local_password
DATABASE_URL=postgresql+psycopg://taskflow:taskflow_local_password@db:5432/taskflow
IMAGE_TAG=local
```

These credentials are only for the local demo. **Never reuse them in production.**

If `.env` is missing, run:

```bash
cp .env.example .env
```

The `.env` file is ignored by Git.

## 6. Run the complete application locally

From the project root:

```bash
docker compose up --build -d
```

Check containers:

```bash
docker compose ps
```

Check logs:

```bash
docker compose logs -f app
```

Open:

```text
http://localhost
```

API documentation:

```text
http://localhost/docs
```

Health endpoint:

```text
http://localhost/health
```

Stop the application:

```bash
docker compose down
```

Delete the local PostgreSQL volume too:

```bash
docker compose down -v
```

## 7. Production `.env` on EC2

Create this file on the EC2 server:

```text
/opt/taskflow/.env
```

Use the following structure:

```env
AWS_REGION=ap-south-1
ECR_REGISTRY=123456789012.dkr.ecr.ap-south-1.amazonaws.com
ECR_REPOSITORY=taskflow
IMAGE_TAG=REPLACE_WITH_GIT_SHA

POSTGRES_DB=taskflow
POSTGRES_USER=taskflow
POSTGRES_PASSWORD=REPLACE_WITH_A_LONG_RANDOM_PASSWORD
DATABASE_URL=postgresql+psycopg://taskflow:REPLACE_WITH_URL_ENCODED_PASSWORD@db:5432/taskflow
```

### Important

Replace:

- `123456789012` with your AWS account ID
- `REPLACE_WITH_GIT_SHA` with the Docker image tag being deployed
- `REPLACE_WITH_A_LONG_RANDOM_PASSWORD` with a strong PostgreSQL password
- The password in `DATABASE_URL` must be URL-encoded if it contains special characters such as `@`, `:`, `/`, `#`, or `%`.

Example using a simple portfolio password:

```env
POSTGRES_PASSWORD=TaskFlowDemo_2026_Strong
DATABASE_URL=postgresql+psycopg://taskflow:TaskFlowDemo_2026_Strong@db:5432/taskflow
```

For a real production workload, do not keep the database password in plaintext on disk. Use AWS Secrets Manager/SSM Parameter Store and inject the secret securely.

## 8. Prepare EC2

Create the application directory:

```bash
sudo mkdir -p /opt/taskflow
sudo chown -R $USER:$USER /opt/taskflow
cd /opt/taskflow
```

Copy the production files into this directory, including:

```text
Docker Compose
Nginx configuration
scripts/
.env
```

The EC2 instance needs access to ECR. The recommended approach is an IAM instance role with the required ECR read permissions.

Test ECR authentication:

```bash
aws ecr get-login-password --region ap-south-1 | \
  docker login --username AWS --password-stdin \
  123456789012.dkr.ecr.ap-south-1.amazonaws.com
```

## 9. Create ECR repository

Create an ECR repository named `taskflow`:

```bash
aws ecr create-repository \
  --repository-name taskflow \
  --region ap-south-1
```

The repository URL will look like:

```text
123456789012.dkr.ecr.ap-south-1.amazonaws.com/taskflow
```

Put the registry and repository in `/opt/taskflow/.env`.

## 10. First production deployment

Once an image has been pushed to ECR, set the image tag:

```bash
export IMAGE_TAG=<git-commit-sha>
```

Then run:

```bash
cd /opt/taskflow
./scripts/deploy.sh
```

The script:

1. Logs Docker into ECR.
2. Pulls the requested image.
3. Starts PostgreSQL.
4. Starts the application.
5. Starts Nginx.
6. Runs the health check.
7. Shows the running containers.

## 11. Single-click GitHub Actions deployment

The GitHub Actions workflow is:

```text
.github/workflows/deploy.yml
```

Workflow:

```text
Push code
   ↓
Checkout
   ↓
Test
   ↓
Build Docker image
   ↓
Push image to ECR
   ↓
AWS SSM Run Command
   ↓
EC2 deploy.sh
   ↓
Health check
```

The workflow can also be started manually using `workflow_dispatch`.

### GitHub configuration

Create an AWS IAM role for GitHub OIDC and configure this repository secret:

```text
AWS_DEPLOY_ROLE_ARN
```

Update these values in `.github/workflows/deploy.yml`:

```yaml
AWS_REGION: ap-south-1
ECR_REPOSITORY: taskflow
EC2_INSTANCE_ID: i-xxxxxxxxxxxxxxxxx
```

Do not put an AWS access key or secret key in the repository.

## 12. Jenkins deployment

The alternative pipeline is:

```text
Jenkinsfile
```

Flow:

```text
Jenkins
   ↓
Checkout
   ↓
Test
   ↓
Docker Build
   ↓
Push to ECR
   ↓
AWS SSM
   ↓
EC2
   ↓
Docker Compose
   ↓
Health Check
```

The Jenkins server needs:

- Docker access
- AWS CLI
- AWS credentials/role with ECR push + SSM permissions
- AWS Credentials/withAWS plugin if using the supplied Jenkinsfile

Update the placeholders in `Jenkinsfile` before using it.

## 13. HTTPS with Nginx

Nginx is the public entry point:

```text
Internet
   ↓
443 HTTPS
   ↓
Nginx
   ↓
FastAPI :8000
```

The production Compose file mounts `/etc/letsencrypt` into Nginx. Obtain a certificate using your preferred certificate-management method and configure the domain in `nginx/conf.d/taskflow.conf`.

For a portfolio demo, you can first run HTTP locally and then enable HTTPS on the EC2/domain deployment.

## 14. Rollback

Every CI/CD build uses the Git commit SHA as the Docker image tag. This makes rollback straightforward.

Example:

```bash
export IMAGE_TAG=<previous-known-good-sha>
./scripts/rollback.sh
```

The rollback script pulls that exact image and verifies the health endpoint.

## 15. Useful troubleshooting commands

```bash
docker compose -f docker-compose.prod.yml ps

docker compose -f docker-compose.prod.yml logs --tail=100 app

docker compose -f docker-compose.prod.yml logs --tail=100 nginx

docker compose -f docker-compose.prod.yml logs --tail=100 db

curl http://localhost/health

docker images
```

Check SSM:

```bash
aws ssm describe-instance-information
```

Check ECR images:

```bash
aws ecr describe-images \
  --repository-name taskflow \
  --region ap-south-1
```

## 16. Production security checklist

- [ ] Do not commit `.env`.
- [ ] Do not put AWS access keys in GitHub/Jenkins/source code.
- [ ] Prefer GitHub OIDC for GitHub Actions.
- [ ] Prefer IAM roles for EC2.
- [ ] Use SSM instead of exposing SSH where practical.
- [ ] Allow HTTP/HTTPS publicly; restrict or remove SSH.
- [ ] Never expose PostgreSQL port 5432 publicly.
- [ ] Use HTTPS.
- [ ] Use ECR image scanning.
- [ ] Use immutable/versioned image tags instead of `latest`.
- [ ] Keep the EC2 host and Docker images patched.
- [ ] Store production secrets in AWS Secrets Manager or Parameter Store.
- [ ] Add monitoring/alarms for a real production deployment.

## 17. Portfolio talking points

This project demonstrates more than simply running Docker. It shows a complete delivery path:

**Application → Docker → Compose → Nginx → HTTPS → AWS EC2 → ECR → CI/CD → SSM → Health Check → Rollback**

That is the workflow to discuss when applying for Docker/AWS deployment freelance jobs.
