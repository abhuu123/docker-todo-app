# Production Deployment Runbook

1. Install Docker, Compose and SSM Agent on EC2.
2. Put the project under `/opt/taskflow`.
3. Configure `/opt/taskflow/.env` without committing it.
4. Configure ECR and an EC2 IAM role allowing ECR pull and SSM.
5. Configure DNS and TLS.
6. Deploy with `IMAGE_TAG=<git-sha> ./scripts/deploy.sh`.
7. Verify `docker compose -f docker-compose.prod.yml ps` and `curl http://localhost/health`.
8. Roll back with `IMAGE_TAG=<previous-good-sha> ./scripts/rollback.sh`.

For real production, use Secrets Manager instead of plaintext database passwords, restrict/remove SSH, enable CloudWatch monitoring, patch EC2, and use GitHub OIDC or equivalent short-lived credentials.
