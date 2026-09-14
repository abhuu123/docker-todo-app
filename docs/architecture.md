# TaskFlow Architecture

## Runtime flow

```text
User
  ↓ HTTPS
Route 53 / DNS
  ↓
AWS EC2
  ↓
Nginx
  ↓
FastAPI application container
  ↓
PostgreSQL container
```

The application and database communicate through a private Docker bridge network. PostgreSQL is not published to the host.

## CI/CD flow

Both pipelines implement the same delivery model:

```text
Developer
   ↓
GitHub
   ↓
┌───────────────────────────────┐
│ GitHub Actions OR Jenkins     │
│ Test → Build → Push to ECR    │
└──────────────┬────────────────┘
               ↓
          Amazon ECR
               ↓
        AWS SSM Run Command
               ↓
             EC2
               ↓
        deploy.sh
               ↓
       Docker Compose
               ↓
         Health Check
               ↓
          Production
```

## Security model

- CI/CD uses OIDC or managed AWS credentials rather than application-level AWS keys.
- EC2 uses an IAM role to pull images from ECR and receive SSM commands.
- PostgreSQL is internal to the Docker network.
- Nginx is the public application entry point.
- Production secrets are externalized from source code.
- Versioned Docker image tags allow deterministic deployments and rollback.
