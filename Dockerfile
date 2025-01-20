FROM python:3.12-slim

WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy the entire project
COPY . .

# Disable virtualenv creation (this is crucial)
ENV POETRY_VIRTUALENVS_CREATE=false

# Install dependencies
RUN poetry install --only main --no-interaction --no-ansi

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
# Note the module path change to reflect the src directory
CMD ["poetry", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]