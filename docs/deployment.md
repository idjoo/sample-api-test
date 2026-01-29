# Deployment

The project is designed to be containerized and deployed to cloud platforms like Google Cloud Run.

## Docker

The `Dockerfile` is optimized for production:

- Multi-stage build.
- Uses `uv` for installation.
- Runs as a non-root user.

**Build Image:**

```sh
docker build -t my-service .
```

**Run Container:**

```sh
docker run -p 8080:8080 my-service
```

## CI/CD (Google Cloud)

Configuration files are included for a standard GCP pipeline:

- **cloudbuild.yaml**: Defines the build steps for Google Cloud Build.
- **skaffold.yaml**: For continuous development and deployment workflows on Kubernetes/Cloud Run.

## Production Checklist

1.  Set `environment: prd` in config.
2.  Ensure `SECRET` variables (DB passwords) are passed via Environment Variables or Secret Manager, not committed in code.
3.  Configure your Cloud Trace/Logging permissions for the service account.
