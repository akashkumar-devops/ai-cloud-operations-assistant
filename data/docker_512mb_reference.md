# Docker operations quick reference

This concise reference supplements the indexed Docker documentation with copyable commands and diagnostic workflows. Replace placeholders before running commands. Run commands from a trusted host and review destructive operations before use.

## Build an image from a Dockerfile
Source: https://docs.docker.com/build/concepts/context/

The Dockerfile is the recipe; the build context is the directory whose files are available to COPY or ADD. From the project directory, create an image tagged with a useful name and version:

```bash
docker build -t my-app:1.0 .
```

Use a non-default Dockerfile or build context explicitly:

```bash
docker build -f docker/Dockerfile -t my-app:1.0 .
```

Use a `.dockerignore` file to keep unnecessary files, local credentials, virtual environments, build output, and version-control data out of the context. For example:

```text
.git
.env
.venv
__pycache__/
node_modules/
dist/
```

The dot at the end of the build command means the current directory is the context. A path outside the context cannot be copied into the image. BuildKit is the standard modern build backend for normal `docker build` use; build options are documented in the Docker Buildx reference.

## Improve Dockerfile caching and image size
Source: https://docs.docker.com/build/building/best-practices/

Arrange Dockerfile instructions so dependency manifests are copied and installed before frequently changing application source. Docker can reuse unchanged layers; a change to an earlier instruction invalidates later layers. Use a multi-stage build to keep compilers and other build-only tools out of the final runtime image.

```dockerfile
FROM python:3.12-slim AS build
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

FROM python:3.12-slim
WORKDIR /app
COPY --from=build /app /app
CMD ["python", "app.py"]
```

This is a starting example, not a universal production Dockerfile. Pin and update base-image versions deliberately, keep the runtime stage minimal, and run the application as a non-root user where practical. To force a fresh base-image check, use `--pull`; to ignore the build cache, use `--no-cache`. These options do different things.

## Run and inspect a container
Source: https://docs.docker.com/reference/cli/docker/container/run/

Start a container in the background, name it, and publish host port 8080 to container port 80:

```bash
docker run -d --name web -p 8080:80 nginx:alpine
```

List running containers and all containers, including stopped ones:

```bash
docker ps
```

```bash
docker ps -a
```

Inspect its configuration and state:

```bash
docker inspect web
```

Run a command inside a running container:

```bash
docker exec -it web sh
```

The `EXPOSE` Dockerfile instruction documents a container port; it does not publish that port to the host. Publishing is done with `-p`. By default, a published port may be reachable on host interfaces; use `-p 127.0.0.1:8080:80` when access should be limited to the local host.

## Diagnose health, logs, events, and resource use
Source: https://docs.docker.com/reference/cli/docker/container/logs/

Follow recent logs with timestamps:

```bash
docker logs --tail 100 --timestamps --follow web
```

Inspect health-check status, exit state, mounts, and network settings:

```bash
docker inspect web
```

Watch container lifecycle and health events while reproducing an issue:

```bash
docker events --filter container=web
```

Check current CPU and memory use:

```bash
docker stats web
```

A Dockerfile `HEALTHCHECK` defines how Docker periodically checks application health. A container can be running while its health status is unhealthy; inspect the health section in `docker inspect` and check the application logs. If no health check is configured, the health status may be absent.

## Connect containers with networks and ports
Source: https://docs.docker.com/engine/network/drivers/bridge/

Create a user-defined bridge network and run two containers on it:

```bash
docker network create app-net
```

```bash
docker run -d --name database --network app-net postgres:16
```

```bash
docker run -d --name api --network app-net my-api:1.0
```

Containers on a user-defined bridge network can resolve one another by container name. Applications on the same network should connect to the other container's name and its listening container port; host-published ports are for access from outside the Docker network. Inspect network membership and addresses:

```bash
docker network inspect app-net
```

If a host client cannot connect, verify the app listens on the expected interface and container port, then verify the host-to-container mapping with `docker ps` or `docker port`. A port mapping cannot fix an application that only listens on the container's loopback interface.

## Persist data with volumes and bind mounts
Source: https://docs.docker.com/engine/storage/

A container's writable layer is tied to the container lifecycle. Use a named volume for data that should outlive a container:

```bash
docker volume create app-data
```

```bash
docker run -d --name database --mount source=app-data,target=/var/lib/postgresql/data postgres:16
```

Use a bind mount when a host directory must be shared with a container, such as source code during local development:

```bash
docker run --rm --mount type=bind,source="$(pwd)/src",target=/app/src my-app:1.0
```

Check the configured mounts with `docker inspect <container>` and inspect a named volume with `docker volume inspect <volume>`. For permission errors, compare the process UID/GID inside the container with ownership and permissions on the mounted host path. Bind mounts refer to paths on the Docker daemon host; with remote daemons those paths are not necessarily on the CLI machine. Avoid deleting a volume until its data is backed up and no needed container depends on it.

## Run a multi-container app with Compose
Source: https://docs.docker.com/compose/

A Compose file describes related services, networks, and volumes in one project. Validate the file and resolved configuration:

```bash
docker compose config
```

Build and start services in the background:

```bash
docker compose up --build -d
```

List services and follow logs:

```bash
docker compose ps
```

```bash
docker compose logs --follow
```

Stop and remove the project's containers and network:

```bash
docker compose down
```

Compose services on the project network can normally reach each other by service name. `docker compose down -v` also removes named volumes and can delete persistent data; use it only when that deletion is intended.

## Authenticate to a registry and publish an image
Source: https://docs.docker.com/reference/cli/docker/login/

Authenticate interactively; do not put a password or access token directly in a command line or commit it to source control:

```bash
docker login
```

Tag a local image for a registry repository, then push it:

```bash
docker tag my-app:1.0 username/my-app:1.0
```

```bash
docker push username/my-app:1.0
```

Pull a specific tag:

```bash
docker pull username/my-app:1.0
```

A `denied` or `unauthorized` error usually requires checking the registry hostname, login identity, repository permissions, and tag. Docker Hub can return HTTP 429 for pull-rate or abuse limits. Authenticate where appropriate, reduce redundant pulls by reusing cached images, and check the current Docker Hub usage policy because limits can change.

## Limit resources, restart behavior, and harden images
Source: https://docs.docker.com/engine/containers/resource_constraints/

Set container memory and CPU limits, and a restart policy:

```bash
docker run -d --name worker --memory 512m --cpus 1.0 --restart unless-stopped my-worker:1.0
```

Check container resource use and configured limits with `docker stats` and `docker inspect`. A restart policy controls daemon restart behavior; it does not repair a crashing application. Review logs and exit state to find the cause.

For image security, prefer minimal trusted base images, keep packages patched, use a non-root runtime user, avoid unnecessary Linux capabilities, and do not bake credentials into image layers or build arguments. Use BuildKit secret mounts for credentials required during a build. Docker Scout can inspect image packages and vulnerabilities and report SBOM or provenance information; review findings and rebuild from updated base images to remediate them. See Docker's security, build-secret, and Scout documentation for current details.
