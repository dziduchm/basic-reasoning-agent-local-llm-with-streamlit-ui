FROM mcr.microsoft.com/devcontainers/python:1-3.12-bullseye

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Set working directory
WORKDIR /app

# Copy Poetry configuration files
COPY pyproject.toml poetry.lock ./

# Configure Poetry and install dependencies globally (no virtualenv)
RUN poetry config virtualenvs.create false \
    && poetry install --no-root

# Copy the rest of the application code
COPY . .

# Set environment variables
ENV PYTHONPATH="/app:$PYTHONPATH"
ENV PORT=8501

# Expose the Streamlit port
EXPOSE 8501

# Command to run the Streamlit app
CMD ["poetry", "run", "streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
