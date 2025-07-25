FROM python:3.11-slim

# Set working directory
WORKDIR /code

# Install system dependencies needed to build sentence-transformers and torch
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    git \
    libffi-dev \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy everything into the container
COPY . /code

# Ensure Python can find the `app` package
ENV PYTHONPATH=/code

# Upgrade pip to latest version first
RUN pip install --upgrade pip

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8000 for the app
EXPOSE 8000

# Run the FastAPI app using Uvicorn
CMD ["sh", "-c", "uvicorn app.api:app --host 0.0.0.0 --port ${PORT:-8000}"]
