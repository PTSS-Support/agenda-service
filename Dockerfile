FROM python:3.12-slim

WORKDIR /app

# Create and set a non-root user
RUN useradd -m -u 1000 python
RUN chown -R python:python /app

# Install poetry
RUN pip install poetry

# Copy the entire project first
COPY . .

USER python

# Configure poetry to not create a virtual environment
RUN poetry config virtualenvs.create false --local

# Install dependencies
RUN poetry install --only main --no-interaction --no-ansi

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["poetry", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]