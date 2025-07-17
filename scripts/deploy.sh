#!/bin/bash

# === CONFIGURATION ===
PROJECT_ID="quick-sonar-302302"
REGION="asia-east1"
SERVICE_NAME="annotation-tool"
REPO_NAME="${SERVICE_NAME}-repo"
IMAGE_NAME="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${SERVICE_NAME}"

# === Hardcoded Project Root ===
PROJECT_ROOT="/home/sean/WebForFileAnnotation"

# === Change to project root ===
cd "$PROJECT_ROOT" || exit 1
echo "📂 Current working directory: $(pwd)"

# === 0. Create Artifact Registry (if not exists) ===
echo "🔍 Checking Artifact Registry: ${REPO_NAME}"
gcloud artifacts repositories describe ${REPO_NAME} --location=${REGION} >/dev/null 2>&1

if [ $? -ne 0 ]; then
  echo "📦 Creating Artifact Registry: ${REPO_NAME}"
  gcloud artifacts repositories create ${REPO_NAME} \
    --repository-format=docker \
    --location=${REGION} \
    --description="Streamlit app registry"
else
  echo "✅ Artifact Registry exists."
fi

# === 1. Build Docker Image ===
echo "🐳 Building Docker image: ${IMAGE_NAME}"
docker build -t ${IMAGE_NAME} .

# === 2. Push Image to Artifact Registry ===
echo "🚀 Pushing image to Artifact Registry..."
docker push ${IMAGE_NAME}

# === 3. Deploy to Cloud Run ===
echo "🚢 Deploying to Cloud Run: ${SERVICE_NAME}"
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_NAME} \
  --region ${REGION} \
  --platform managed \
  --allow-unauthenticated \
  --port 8501

echo "✅ Deployment complete: ${SERVICE_NAME}"

# === 4. Clean up local Docker image ===
echo "🧹 Cleaning up local Docker image..."
docker rmi ${IMAGE_NAME} || echo "⚠️ Failed to remove image ${IMAGE_NAME}"
