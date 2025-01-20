FROM python:3.12-slim

WORKDIR /app

# Create non-root user
RUN useradd -m -u 1000 python

# Install dependencies first
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY . .
RUN chown -R python:python /app

# Switch to non-root user
USER python

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]