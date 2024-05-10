# This Dockerfile is used to deploy a simple single-container Reflex app instance.
FROM python:3.11

# Copy local context to `/app` inside container (see .dockerignore)
WORKDIR /app

# Install app requirements and reflex in the container
RUN --mount=type=cache,target=/root/.cache pip install reflex

COPY . .

# Needed until Reflex properly passes SIGTERM on backend.
STOPSIGNAL SIGKILL

# Download all npm dependencies and compile frontend
# Always apply migrations before starting the backend.
# CMD [ -d alembic ] && reflex export --frontend-only --no-zip && reflex db migrate; reflex run
RUN reflex init
CMD reflex run -v
