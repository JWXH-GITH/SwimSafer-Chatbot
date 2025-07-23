FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy application code
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the LangGraph workflow

CMD ["python", "main.py", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]