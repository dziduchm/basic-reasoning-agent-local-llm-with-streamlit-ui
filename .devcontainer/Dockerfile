FROM mcr.microsoft.com/devcontainers/python:1-3.12-bullseye

# Install dependencies
RUN apt-get update && apt-get install -y curl

# Install Poetry as root and ensure permissions
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && chmod +x /root/.local/bin/poetry \
    && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Set PATH and PYTHONPATH for all users
ENV PATH="/root/.local/bin:/usr/local/bin:$PATH"
ENV PYTHONPATH="/app:$PYTHONPATH"

# Configure Poetry to install dependencies globally (no virtualenv)
RUN poetry config virtualenvs.create false

# Set working directory before copying files
WORKDIR /app