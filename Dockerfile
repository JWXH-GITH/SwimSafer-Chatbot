FROM python:3.11-slim

# Set working directory
WORKDIR /code

# Copy everything into the container
COPY . /code

# Ensure Python can find the `app` package
ENV PYTHONPATH=/code

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the FastAPI app using Uvicorn
CMD ["sh", "-c", "uvicorn app.api:app --host 0.0.0.0 --port ${PORT:-8000}"]

