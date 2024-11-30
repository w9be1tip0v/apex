# .devcontainer/Dockerfile

# Use the official Python image as the base
FROM python:3.9-slim

# Install necessary system packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /workspace

# Create a non-root user
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && apt-get update && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Set non-interactive mode
ENV DEBIAN_FRONTEND=noninteractive

# Upgrade pip
RUN pip install --upgrade pip

# Install uv
RUN pip install uv

# Switch to the non-root user
USER $USERNAME

# Copy requirements.txt and install dependencies
COPY --chown=$USERNAME:$USERNAME requirements.txt .