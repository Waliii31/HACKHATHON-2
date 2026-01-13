# Todo Application Backend

This is the backend service for the Todo application, built with FastAPI and SQLModel.

## Tech Stack
- **Framework**: FastAPI
- **Database**: PostgreSQL (via SQLModel)
- **Authentication**: JWT-based
- **Database Provider**: Neon Serverless PostgreSQL

## Features
- Full CRUD operations for tasks
- JWT-based authentication and authorization
- User isolation for data security
- RESTful API design
- Async database operations

## Installation

1. Clone the repository
2. Navigate to the backend directory
3. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
4. Activate the virtual environment:
   ```bash
   # On Windows
   venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```
5. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Environment Variables

Create a `.env` file in the backend directory with the following variables:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/todo_db

# JWT
JWT_SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

## Running the Application

1. Make sure your environment variables are set
2. Run the application:
   ```bash
   python -m app.main
   ```
3. The API will be available at `http://localhost:8000`

## API Documentation

Auto-generated API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Database Migrations

To create a new migration:
```bash
alembic revision --autogenerate -m "Description of changes"
```

To apply migrations:
```bash
alembic upgrade head
```

## Testing

Run the tests:
```bash
pytest
```