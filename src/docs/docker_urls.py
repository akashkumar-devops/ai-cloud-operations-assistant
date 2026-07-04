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
    "docker_install": "https://docs.docker.com/engine/install/",

    # =====================================================
    # Docker Engine
    # =====================================================

    "docker_engine": "https://docs.docker.com/engine/",
    "docker_desktop": "https://docs.docker.com/desktop/",

    # =====================================================
    # Images & Dockerfile
    # =====================================================

    "dockerfile": "https://docs.docker.com/reference/dockerfile/",
    "build_images": "https://docs.docker.com/build/building/",
    "multi_stage_builds": "https://docs.docker.com/build/building/multi-stage/",
    "build_cache": "https://docs.docker.com/build/cache/",

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

    # =====================================================
    # Docker Compose
    # =====================================================

    "docker_compose": "https://docs.docker.com/compose/",
    "compose_file_reference": "https://docs.docker.com/reference/compose-file/",

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
    # Logging
    # =====================================================

    "docker_logging": "https://docs.docker.com/engine/logging/",
}