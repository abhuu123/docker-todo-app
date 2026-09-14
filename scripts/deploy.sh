#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/taskflow}"
cd "$APP_DIR"

# docker compose reads .env automatically for interpolation.
# Read only deployment variables from .env without sourcing the whole file.
read_env() {
  local key="$1"
  local value
  value="$(grep -E "^${key}=" .env 2>/dev/null | tail -n1 | cut -d= -f2- || true)"
  printf '%s' "$value"
}

IMAGE_TAG="${IMAGE_TAG:-$(read_env IMAGE_TAG)}"
AWS_REGION="${AWS_REGION:-$(read_env AWS_REGION)}"
ECR_REGISTRY="${ECR_REGISTRY:-$(read_env ECR_REGISTRY)}"
ECR_REPOSITORY="${ECR_REPOSITORY:-$(read_env ECR_REPOSITORY)}"

: "${IMAGE_TAG:?IMAGE_TAG is required}"
: "${AWS_REGION:?AWS_REGION is required in .env or environment}"
: "${ECR_REGISTRY:?ECR_REGISTRY is required in .env or environment}"
: "${ECR_REPOSITORY:?ECR_REPOSITORY is required in .env or environment}"

export IMAGE_TAG AWS_REGION ECR_REGISTRY ECR_REPOSITORY

command -v aws >/dev/null || { echo "ERROR: AWS CLI is not installed."; exit 1; }
command -v docker >/dev/null || { echo "ERROR: Docker is not installed."; exit 1; }

IMAGE="${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}"

echo "Logging in to ECR..."
aws ecr get-login-password --region "$AWS_REGION" \
  | docker login --username AWS --password-stdin "$ECR_REGISTRY"

echo "Deploying ${IMAGE}..."
docker compose -f docker-compose.prod.yml pull app
docker compose -f docker-compose.prod.yml up -d db app nginx

if ! ./scripts/health-check.sh "http://localhost/health"; then
  echo "ERROR: New deployment failed health check."
  echo "Inspect logs with: docker compose -f docker-compose.prod.yml logs --tail=100"
  echo "Restore the previous known-good tag with scripts/rollback.sh."
  exit 1
fi

echo "Deployment successful: ${IMAGE}"
docker compose -f docker-compose.prod.yml ps
