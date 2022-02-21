
docker build --platform linux/amd64 -f ./ingestion-module/Dockerfile_prod -t ghcr.io/seanjin97/watersense-ingestion:latest ingestion-module
# docker push ghcr.io/seanjin97/watersense-ingestion:latest