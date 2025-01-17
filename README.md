# Agenda Service

### NOTE; SWAGGER DOES **NOT** SEND THE COOKIE CORRECTLY, MUST USE INSOMNIA OR OTHER ALTERNATIVES TO SEND CURL COMMANDS
A FastAPI-based microservice for managing group-based agenda items with JWT authentication via Keycloak.

## Overview

This service manages agenda items for different groups, using Azure Table Storage as its database. Authentication is handled through Keycloak JWT tokens, though the service only uses Keycloak's public key for token validation (no direct connection to Keycloak required).

## Prerequisites

- Python 3.12 or higher
- Poetry (Python package manager)
- Azure Table Storage account (for storing agenda items)
- Keycloak public key (for JWT validation)

## Getting Started

1. Clone the repository
2. Install dependencies:
   ```bash
   poetry install
   ```
3. Create a `.env` file in the root directory with the following variables:
   ```env
   HOST=0.0.0.0
   PORT=8000
   LOG_LEVEL=info
   KEYCLOAK_PUBLIC_KEY=your_public_key_here
   JWT_VALIDATION_ENABLED=true
   ```
4. Start the development server:
   ```bash
   poetry run uvicorn src.main:app --reload
   ```
   The `--reload` flag enables auto-reload on code changes (development only)

## Project Structure Explanation

This project uses dependency injection to maintain clean, testable code. Here's how it works:

### Dependency Injection Example

```python
# Instead of directly creating dependencies:
@app.get("/agenda/items")
async def list_items():
    facade = AgendaFacade()  # Direct creation (not recommended)
    return facade.list_items()

# We use FastAPI's dependency injection:
@app.get("/agenda/items")
async def list_items(
    facade: AgendaFacade = Depends(get_agenda_facade)
):
    return facade.list_items()
```

The benefits of this approach:
- Easier testing through dependency mocking
- Better separation of concerns
- More maintainable code
- Dependencies can be reused across different endpoints

### Error Handling

The service includes centralized error handling through FastAPI's exception handlers. All errors are properly logged and return standardized error responses to clients.

## Service Flow

### Authentication Flow
- The service never connects directly to Keycloak
- Instead, it uses Keycloak's public key to validate JWT tokens locally
- Each request must include a JWT token containing the group_id
- The JWT token is validated using the public key before any operation

### Main Operations

1. **List Items**
   - Client sends GET request with date range and JWT
   - Service validates JWT and extracts group_id
   - Returns filtered agenda items for that group

2. **Create Item**
   - Client sends POST request with item details and JWT
   - Service validates JWT and extracts group_id
   - Creates new item in Azure Table Storage

3. **Update/Delete Item**
   - Client sends PUT/DELETE request with item ID and JWT
   - Service validates JWT and verifies group ownership
   - Updates/Deletes item in Azure Table Storage

## Sequence Diagrams
https://claude.site/artifacts/5c09569a-d0e7-4788-915b-c131739b4b81

The diagram shows the three main flows:
1. Listing items (blue)
2. Creating items (green)
3. Updating/Deleting items (red)

Note: While the diagram shows Keycloak as a separate service, our service only uses Keycloak's public key for JWT validation. **There's no direct communication with a Keycloak server**.

## API Documentation

When the service is running, visit `/docs` for the complete OpenAPI documentation of all endpoints.


# NOTE; SWAGGER DOES **NOT** SEND THE COOKIE CORRECTLY, MUST USE INSOMNIA OR OTHER ALTERNATIVES TO SEND CURL COMMANDS
