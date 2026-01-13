# Todo Application - Technical Architecture

## Overview
This document outlines the complete technical architecture for Phase II of the Todo Full-Stack Web Application. The architecture follows a monorepo pattern with a clear separation of concerns between frontend and backend responsibilities, while maintaining tight integration through a well-defined API layer.

## Monorepo Layout

### Project Structure
```
todo-app/
├── pnpm-workspace.yaml          # Workspace configuration for monorepo
├── package.json                # Root package management
├── .env.example               # Example environment variables
├── .gitignore                 # Git ignore rules
├── README.md                  # Project documentation
├── frontend/                  # Next.js frontend application
│   ├── package.json           # Frontend dependencies
│   ├── tsconfig.json          # TypeScript configuration
│   ├── next.config.js         # Next.js configuration
│   ├── .env.local             # Local environment variables
│   ├── public/                # Static assets
│   ├── app/                   # Next.js App Router pages
│   │   ├── layout.tsx         # Root layout
│   │   ├── page.tsx           # Home page
│   │   ├── login/page.tsx     # Login page
│   │   ├── signup/page.tsx    # Signup page
│   │   ├── dashboard/page.tsx # Task list page
│   │   └── ...                # Other pages
│   ├── components/            # Reusable UI components
│   │   ├── TaskItem.tsx       # Task item component
│   │   ├── TaskForm.tsx       # Task form component
│   │   ├── Navigation.tsx     # Navigation component
│   │   └── ...                # Other components
│   ├── lib/                   # Utility functions and API clients
│   │   ├── auth.ts            # Better Auth integration
│   │   ├── api-client.ts      # API communication utilities
│   │   └── utils.ts           # General utilities
│   ├── types/                 # TypeScript type definitions
│   │   ├── task.ts            # Task-related types
│   │   ├── user.ts            # User-related types
│   │   └── api.ts             # API response types
│   └── styles/                # Global styles
├── backend/                   # FastAPI backend application
│   ├── requirements.txt       # Python dependencies
│   ├── alembic.ini            # Database migration configuration
│   ├── .env                   # Local environment variables
│   ├── app/                   # Main application package
│   │   ├── main.py            # FastAPI application entry point
│   │   ├── config.py          # Application configuration
│   │   ├── database/          # Database connection and session management
│   │   │   ├── connection.py  # Database connection utilities
│   │   │   ├── session.py     # Database session management
│   │   │   └── models.py      # SQLModel database models
│   │   ├── models/            # SQLModel database models
│   │   │   ├── user.py        # User model
│   │   │   ├── task.py        # Task model
│   │   │   └── __init__.py    # Models module initialization
│   │   ├── schemas/           # Pydantic schemas for validation
│   │   │   ├── user.py        # User-related schemas
│   │   │   ├── task.py        # Task-related schemas
│   │   │   └── __init__.py    # Schemas module initialization
│   │   ├── api/               # API route definitions
│   │   │   ├── deps.py        # Dependency injection utilities
│   │   │   ├── auth.py        # Authentication-related endpoints
│   │   │   ├── tasks.py       # Task-related endpoints
│   │   │   └── __init__.py    # API module initialization
│   │   ├── auth/              # Authentication logic
│   │   │   ├── jwt.py         # JWT handling utilities
│   │   │   └── security.py    # Security utilities
│   │   └── core/              # Core application logic
│   │       ├── exceptions.py  # Custom exception definitions
│   │       └── utils.py       # Core utilities
├── tests/                     # Test files
│   ├── frontend/              # Frontend tests
│   └── backend/               # Backend tests
└── docs/                      # Additional documentation
```

## Frontend Responsibilities

### Application Framework
- **Framework**: Next.js 14+ with App Router
- **Language**: TypeScript for type safety
- **Styling**: Tailwind CSS for utility-first styling
- **Package Manager**: pnpm for efficient monorepo management

### Authentication Management
- **Primary Tool**: Better Auth for frontend authentication
- **Session Handling**: Client-side session management
- **Token Storage**: Secure storage of JWT tokens (HTTP-only cookies or secure localStorage)
- **Route Protection**: Auth Guard component to protect private routes
- **User State**: Maintain user authentication state across the application

### API Communication
- **Client**: Built-in fetch API or axios for HTTP requests
- **Authorization**: Attach JWT tokens to API requests in Authorization header
- **Error Handling**: Handle API errors and authentication failures
- **Loading States**: Manage loading states during API operations
- **Retry Logic**: Implement retry mechanisms for failed requests

### UI/UX Implementation
- **Component Library**: Reusable components as specified in UI specs
- **Page Routing**: Next.js App Router for client-side navigation
- **State Management**: React Context API or Zustand for application state
- **Form Handling**: Proper validation and submission handling
- **Responsive Design**: Mobile-first responsive design approach

### Data Management
- **Local State**: React state for UI-specific data
- **Global State**: Context or Zustand for application-wide data
- **Caching**: Implement caching strategies for improved performance
- **Optimistic Updates**: Update UI before server confirmation when appropriate

## Backend Responsibilities

### Application Framework
- **Framework**: FastAPI for high-performance Python web API
- **Language**: Python 3.9+ with type hints
- **Documentation**: Automatic OpenAPI/Swagger documentation
- **Async Support**: Asynchronous request handling

### Database Management
- **ORM**: SQLModel for PostgreSQL database operations
- **Models**: Define database models matching schema specifications
- **Sessions**: Database session management with proper connection pooling
- **Migrations**: Alembic for database schema migrations
- **Transactions**: Proper transaction handling for data consistency

### API Layer
- **Endpoints**: RESTful API endpoints as specified in API specs
- **Validation**: Pydantic schemas for request/response validation
- **Authentication**: JWT token verification for protected endpoints
- **Error Handling**: Proper HTTP status codes and error responses
- **Rate Limiting**: Implement rate limiting for API protection

### Security Implementation
- **JWT Verification**: Validate JWT tokens for authenticated requests
- **Input Sanitization**: Sanitize inputs to prevent injection attacks
- **CORS Policy**: Configure appropriate CORS settings
- **Security Headers**: Implement security headers for protection
- **Access Control**: Verify user ownership of resources

### Business Logic
- **Service Layer**: Encapsulate business logic in service modules
- **Validation**: Implement business rule validation
- **Error Handling**: Handle business logic errors appropriately
- **Logging**: Implement proper logging for debugging and monitoring

## Authentication Flow (JWT Lifecycle)

### Initial Authentication
1. User provides credentials on login/signup page
2. Frontend sends credentials to Better Auth
3. Better Auth validates credentials and creates session
4. Better Auth generates JWT token and stores in secure cookie/storage
5. Frontend receives authentication state update
6. User is redirected to protected area

### API Request Flow
1. Frontend prepares API request to backend
2. Frontend retrieves JWT token from session
3. Frontend adds Authorization header: `Bearer <jwt_token>`
4. Request is sent to backend API endpoint
5. Backend extracts JWT token from Authorization header
6. Backend verifies JWT signature and validity
7. Backend extracts user ID from token claims
8. Backend validates user existence and active status
9. Backend processes request with user context
10. Backend returns response to frontend

### Token Refresh Process
1. Frontend monitors JWT expiration time
2. Before token expires, Better Auth automatically refreshes if needed
3. New JWT token is stored securely
4. Subsequent API requests use new token

### Session Termination
1. User clicks logout button
2. Frontend calls Better Auth logout function
3. Better Auth clears session and tokens
4. Frontend redirects to login page
5. Backend tokens become invalid after expiration

## Data Flow from UI → API → DB

### Task Creation Flow
1. User fills task form in UI (Task Form component)
2. Form validation occurs client-side
3. Frontend sends POST request to `/api/v1/users/{user_id}/tasks`
4. Request includes JWT token in Authorization header
5. Backend verifies JWT and user authentication
6. Backend validates request body using Pydantic schema
7. Backend checks user ownership (user_id matches token subject)
8. Backend creates new Task record in PostgreSQL via SQLModel
9. Backend returns created task object in response
10. Frontend receives response and updates UI with new task

### Task Retrieval Flow
1. Frontend sends GET request to `/api/v1/users/{user_id}/tasks`
2. Request includes JWT token in Authorization header
3. Backend verifies JWT and extracts user ID
4. Backend queries PostgreSQL for tasks belonging to user ID
5. Backend applies filters and pagination as requested
6. Backend returns task list in response
7. Frontend receives response and renders task list

### Task Update Flow
1. User modifies task in UI (Task Form component)
2. Form validation occurs client-side
3. Frontend sends PUT request to `/api/v1/users/{user_id}/tasks/{id}`
4. Request includes JWT token in Authorization header
5. Backend verifies JWT and user authentication
6. Backend validates request body using Pydantic schema
7. Backend verifies task belongs to authenticated user
8. Backend updates Task record in PostgreSQL via SQLModel
9. Backend returns updated task object in response
10. Frontend receives response and updates UI with modified task

### Task Deletion Flow
1. User triggers delete action in UI (Task Item component)
2. Frontend sends DELETE request to `/api/v1/users/{user_id}/tasks/{id}`
3. Request includes JWT token in Authorization header
4. Backend verifies JWT and user authentication
5. Backend verifies task belongs to authenticated user
6. Backend deletes Task record from PostgreSQL via SQLModel
7. Backend returns 204 No Content response
8. Frontend receives response and removes task from UI

## Environment Variables Required

### Frontend Environment Variables
- `NEXT_PUBLIC_BETTER_AUTH_URL`: Better Auth API endpoint URL
- `NEXT_PUBLIC_BETTER_AUTH_TOKEN`: Better Auth API token
- `NEXT_PUBLIC_API_BASE_URL`: Backend API base URL
- `NEXT_PUBLIC_JWT_SECRET`: Secret for JWT verification (if needed client-side)
- `NEXT_PUBLIC_APP_NAME`: Application name for display

### Backend Environment Variables
- `DATABASE_URL`: PostgreSQL connection string for Neon database
- `JWT_SECRET_KEY`: Secret key for signing JWT tokens
- `JWT_ALGORITHM`: Algorithm for JWT signing (default: HS256)
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time in minutes
- `DATABASE_POOL_SIZE`: Database connection pool size
- `DATABASE_POOL_TIMEOUT`: Database connection timeout
- `ALLOWED_ORIGINS`: Comma-separated list of allowed origins for CORS
- `LOG_LEVEL`: Logging level for the application (default: INFO)
- `ENVIRONMENT`: Environment identifier (dev, staging, prod)

### Database Environment Variables
- `NEON_PROJECT_ID`: Neon project identifier
- `NEON_DATABASE_NAME`: Database name in Neon
- `NEON_DATABASE_USER`: Database user credentials
- `NEON_DATABASE_PASSWORD`: Database password
- `NEON_DATABASE_HOST`: Database host URL

### Development Environment Variables
- `DEV_MODE`: Flag to enable development-specific features
- `DEBUG_LOGGING`: Flag to enable verbose logging
- `TEST_DATABASE_URL`: Separate database URL for testing