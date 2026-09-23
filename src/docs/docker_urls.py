"""
Filename: docker_urls.py

Purpose:
---------
Contains all Docker documentation URLs used by the scraper.

Keeping URLs in a separate file makes it easy to:
- Add new Docker documentation
- Remove outdated pages
- Support Kubernetes/OpenShift/Helm later

Used By:
--------
- scraper.py

Project:
--------
AI Cloud Operations Assistant
"""

DOCKER_URLS = {

    # =====================================================
    # Getting Started
    # =====================================================

    "docker_get_started": "https://docs.docker.com/get-started/",
    "docker_overview": "https://docs.docker.com/get-started/docker-overview/",
    "docker_install": "https://docs.docker.com/engine/install/",

    # =====================================================
    # Docker Engine
    # =====================================================

    "docker_engine": "https://docs.docker.com/engine/",
    "docker_desktop": "https://docs.docker.com/desktop/",
    "engine_daemon": "https://docs.docker.com/engine/daemon/",
    "daemon_logs": "https://docs.docker.com/engine/daemon/logs/",
    "engine_cli_reference": "https://docs.docker.com/reference/cli/docker/",
    "daemon_cli_reference": "https://docs.docker.com/reference/cli/dockerd/",
    "engine_api_reference": "https://docs.docker.com/reference/api/",
    "resource_pruning": "https://docs.docker.com/engine/manage-resources/pruning/",

    # =====================================================
    # Images & Dockerfile
    # =====================================================

    "dockerfile": "https://docs.docker.com/reference/dockerfile/",
    "build_images": "https://docs.docker.com/build/",
    "multi_stage_builds": "https://docs.docker.com/build/building/multi-stage/",
    "build_cache": "https://docs.docker.com/build/cache/",
    "build_overview": "https://docs.docker.com/build/concepts/overview/",
    "build_context": "https://docs.docker.com/build/concepts/context/",
    "build_secrets": "https://docs.docker.com/build/building/secrets/",
    "build_variables": "https://docs.docker.com/build/building/variables/",
    "multi_platform_builds": "https://docs.docker.com/build/building/multi-platform/",
    "buildkit": "https://docs.docker.com/build/buildkit/",
    "build_cache_backends": "https://docs.docker.com/build/cache/backends/",

    # =====================================================
    # Containers
    # =====================================================

    "containers_run": "https://docs.docker.com/engine/containers/run/",
    "containers_restart": "https://docs.docker.com/engine/containers/start-containers-automatically/",
    "resource_constraints": "https://docs.docker.com/engine/containers/resource_constraints/",

    # =====================================================
    # Storage
    # =====================================================

    "volumes": "https://docs.docker.com/engine/storage/volumes/",
    "bind_mounts": "https://docs.docker.com/engine/storage/bind-mounts/",

    # =====================================================
    # Networking
    # =====================================================

    "networking": "https://docs.docker.com/engine/network/",
    "bridge_network": "https://docs.docker.com/engine/network/drivers/bridge/",
    "port_publishing": "https://docs.docker.com/engine/network/port-publishing/",

    # =====================================================
    # Docker Compose
    # =====================================================

    "docker_compose": "https://docs.docker.com/compose/",
    "compose_file_reference": "https://docs.docker.com/reference/compose-file/",
    "compose_profiles": "https://docs.docker.com/compose/how-tos/profiles/",
    "compose_startup_order": "https://docs.docker.com/compose/how-tos/startup-order/",
    "compose_networking": "https://docs.docker.com/compose/how-tos/networking/",
    "compose_secrets": "https://docs.docker.com/compose/how-tos/use-secrets/",
    "compose_environment_variables": "https://docs.docker.com/compose/how-tos/environment-variables/set-environment-variables/",

    # =====================================================
    # Docker Hub
    # =====================================================

    "docker_hub": "https://docs.docker.com/docker-hub/",

    # =====================================================
    # Security
    # =====================================================

    "docker_security": "https://docs.docker.com/engine/security/",
    "rootless_docker": "https://docs.docker.com/engine/security/rootless/",

    # =====================================================
    # Storage Drivers and Containerd Image Store
    # =====================================================

    "storage_drivers": "https://docs.docker.com/engine/storage/drivers/",
    "containerd_image_store": "https://docs.docker.com/engine/storage/containerd/",

    # =====================================================
    # Logging
    # =====================================================

    "docker_logging": "https://docs.docker.com/engine/logging/",
}
