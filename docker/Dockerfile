FROM python:3.12-slim

LABEL maintainer="Kitchen Layout Generator"
LABEL description="Kitchen layout and design project with ASCII and SVG visualization"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Copy project files
COPY pyproject.toml poetry.lock* ./
COPY scripts/ ./scripts/
COPY README.md ./

# Configure Poetry to not create virtual environments (we're in a container)
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-interaction --no-ansi --no-root

# Install the project itself
RUN poetry install --no-interaction --no-ansi

# Create output directory
RUN mkdir -p /app/output

# Set Python path
ENV PYTHONPATH=/app

# Default command - generate SVG layout
CMD ["python", "scripts/engine/svg_renderer.py"]
