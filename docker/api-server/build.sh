
docker build --platform linux/amd64 -f ./api-server/Dockerfile_prod -t ghcr.io/seanjin97/watersense-api:latest .
# docker push ghcr.io/seanjin97/watersense-api:latest