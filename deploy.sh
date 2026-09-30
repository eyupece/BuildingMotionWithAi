#!/bin/bash
# Pull the latest code and deploy to Cloud Run.
#
#   ./deploy.sh                 backend + frontend, keeps the current event
#   ./deploy.sh kastamonu       switch the event and deploy both
#   ./deploy.sh trabzon backend only the backend
#   ./deploy.sh none            original codelab look, no event
set -e
cd "$(dirname "$0")"

EVENT=""
ONLY=""
for arg in "$@"; do
  case "$arg" in
    backend|frontend) ONLY="$arg" ;;
    *) EVENT="$arg" ;;
  esac
done

git pull --ff-only
set -a; source .env; set +a
REGION="${GOOGLE_CLOUD_LOCATION:-us-central1}"

FRONTEND_URL=$(gcloud run services describe gemini-motion-lab-frontend --region "$REGION" \
  --project "$GOOGLE_CLOUD_PROJECT" --format="value(status.url)" 2>/dev/null || true)

if [ "$ONLY" != "frontend" ]; then
  echo "Deploying backend..."
  (cd backend && gcloud run deploy gemini-motion-lab-backend --source . --region "$REGION" \
    --allow-unauthenticated --min-instances 1 --max-instances 3 --memory 2Gi --port 8080 \
    --project "$GOOGLE_CLOUD_PROJECT" --quiet \
    --set-env-vars "GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT,GOOGLE_CLOUD_LOCATION=$GOOGLE_CLOUD_LOCATION,GCS_BUCKET=$GCS_BUCKET,GCS_SIGNING_SA=$GCS_SIGNING_SA,GOOGLE_GENAI_USE_VERTEXAI=$GOOGLE_GENAI_USE_VERTEXAI,MOCK_AI=$MOCK_AI,PUBLIC_BASE_URL=${FRONTEND_URL:-$PUBLIC_BASE_URL}")
fi

if [ "$ONLY" != "backend" ]; then
  BACKEND_URL=$(gcloud run services describe gemini-motion-lab-backend --region "$REGION" \
    --project "$GOOGLE_CLOUD_PROJECT" --format="value(status.url)")
  [ "$EVENT" = "none" ] && EVENT=" "
  if [ -n "$EVENT" ]; then
    CURRENT_EVENT=$(echo "$EVENT" | xargs)
  else
    CURRENT_EVENT=$(grep -s '^VITE_EVENT=' frontend/.env | cut -d= -f2 || true)
  fi
  printf 'VITE_API_BASE=%s\nVITE_EVENT=%s\n' "$BACKEND_URL" "$CURRENT_EVENT" > frontend/.env
  echo "Deploying frontend (event: ${CURRENT_EVENT:-none})..."
  (cd frontend && gcloud run deploy gemini-motion-lab-frontend --source . --region "$REGION" \
    --allow-unauthenticated --min-instances 1 --max-instances 3 --port 8080 \
    --project "$GOOGLE_CLOUD_PROJECT" --quiet)
fi

echo ""
echo "Done: $(gcloud run services describe gemini-motion-lab-frontend --region "$REGION" --project "$GOOGLE_CLOUD_PROJECT" --format='value(status.url)')"
