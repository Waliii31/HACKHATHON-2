# Todo Full-Stack Web Application - Phase II

A complete full-stack Todo application following spec-driven development principles. This project demonstrates modern web development practices with a Next.js frontend and FastAPI backend, integrated with Neon PostgreSQL and Better Auth for authentication.

## Overview

**Phase II** focuses on delivering a production-ready full-stack Todo application with:
- User authentication and authorization
- Complete CRUD operations for tasks
- Responsive user interface
- Secure API endpoints
- Cloud-ready deployment

## Technology Stack

| Component | Technology |
|-----------|-----------|
| **Frontend Framework** | Next.js 14 (App Router) |
| **Frontend Language** | TypeScript |
| **Styling** | Tailwind CSS |
| **Authentication (Frontend)** | Better Auth |
| **Backend Framework** | FastAPI |
| **Backend Language** | Python 3.9+ |
| **Database ORM** | SQLModel |
| **Database** | Neon Serverless PostgreSQL |
| **API Authentication** | JWT (JSON Web Tokens) |
| **Package Manager** | pnpm (monorepo) |

## Project Structure

```
Phase-2/
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── api/            # API endpoints (auth, tasks, health)
│   │   ├── auth/           # Authentication utilities (JWT)
│   │   ├── models/         # SQLModel database models
│   │   ├── schemas/        # Pydantic request/response schemas
│   │   ├── database/       # Database connection and session
│   │   ├── config.py       # Configuration management
│   │   └── main.py         # FastAPI application setup
│   ├── alembic/            # Database migrations
│   ├── requirements.txt    # Python dependencies
│   └── .env.example        # Environment variables template
│
├── frontend/               # Next.js application
│   ├── app/               # Next.js app directory
│   │   ├── page.tsx       # Home page (redirects based on auth)
│   │   ├── login/         # Login page
│   │   ├── signup/        # Signup page
│   │   ├── dashboard/     # Task management dashboard
│   │   └── layout.tsx     # Root layout with providers
│   ├── components/        # React components
│   │   ├── auth-guard.tsx # Protected route component
│   │   ├── navigation.tsx # Header navigation
│   │   ├── task-form.tsx  # Task creation/editing form
│   │   └── task-item.tsx  # Individual task display
│   ├── contexts/          # React Context providers
│   │   └── auth-context.tsx # Authentication state management
│   ├── lib/               # Utility functions
│   │   └── api-client.ts  # API client for backend communication
│   ├── types/             # TypeScript type definitions
│   ├── tsconfig.json      # TypeScript configuration
│   ├── tailwind.config.js # Tailwind CSS configuration
│   ├── package.json       # Dependencies and scripts
│   └── .env.example       # Environment variables template
│
└── README.md             # This file
```

## Features

### User Management
- User registration with email and password
- User login with JWT token generation
- User profile information
- Secure session handling

### Task Operations
- **Create** new tasks with title, description, priority, and due date
- **Read** tasks with filtering (status, priority) and pagination
- **Update** task details and status
- **Delete** tasks
- **Complete** tasks with completion timestamp tracking

### User Interface
- Responsive design for desktop and mobile
- Intuitive navigation and user experience
- Real-time task updates
- Task filtering by status (active/completed) and priority (low/medium/high)
- Beautiful UI with Tailwind CSS

### Security
- JWT-based authentication
- User data isolation (users can only access their own tasks)
- CORS protection
- Password hashing with bcrypt
- Secure token verification

### API Features
- RESTful API design
- Proper HTTP status codes
- Comprehensive error handling
- Pagination support for task lists
- OpenAPI/Swagger documentation

## Setup Instructions

### Prerequisites
- Node.js 18+ and npm/pnpm
- Python 3.9+
- PostgreSQL 12+ (or Neon database account)
- Git

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd Phase-2/backend
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your database URL and settings
   ```

5. **Set up database:**
   ```bash
   # Apply Alembic migrations
   alembic upgrade head
   ```

6. **Run the backend server:**
   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at `http://localhost:8000`
   API documentation: `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd Phase-2/frontend
   ```

2. **Install dependencies:**
   ```bash
   pnpm install  # or npm install
   ```

3. **Configure environment variables:**
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your API base URL
   ```

4. **Run the development server:**
   ```bash
   pnpm dev  # or npm run dev
   ```

   The frontend will be available at `http://localhost:3000`

### Database Setup

#### Using Neon PostgreSQL (Recommended)
1. Create a Neon project at [https://neon.tech](https://neon.tech)
2. Copy the database connection string
3. Add it to your `.env` file as `DATABASE_URL`

#### Using Local PostgreSQL
1. Create a new database:
   ```bash
   createdb todo_db
   ```

2. Update `DATABASE_URL` in `.env`:
   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/todo_db
   ```

## API Documentation

### Authentication Endpoints

**Register User**
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "name": "User Name",
  "password": "securepassword"
}

Response: 201 Created
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user_id": "uuid"
}
```

**Login User**
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword"
}

Response: 200 OK
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user_id": "uuid"
}
```

### Task Endpoints

All task endpoints require authentication via JWT token in the `Authorization` header:
```
Authorization: Bearer <access_token>
```

**Get Tasks List**
```http
GET /api/v1/users/{user_id}/tasks?limit=50&offset=0&status=active&priority=high
Authorization: Bearer <token>

Response: 200 OK
{
  "tasks": [
    {
      "id": "uuid",
      "title": "Task Title",
      "description": "Task description",
      "status": "active",
      "priority": "high",
      "due_date": "2024-12-31T00:00:00",
      "completed_at": null,
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00",
      "user_id": "uuid"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total": 10,
    "has_next": false,
    "has_prev": false
  }
}
```

**Create Task**
```http
POST /api/v1/users/{user_id}/tasks
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "New Task",
  "description": "Task description",
  "priority": "medium",
  "due_date": "2024-12-31T00:00:00"
}

Response: 201 Created
{
  "id": "uuid",
  "title": "New Task",
  ...
}
```

**Get Single Task**
```http
GET /api/v1/users/{user_id}/tasks/{task_id}
Authorization: Bearer <token>

Response: 200 OK
{ task object }
```

**Update Task**
```http
PUT /api/v1/users/{user_id}/tasks/{task_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Updated Title",
  "status": "completed"
}

Response: 200 OK
{ updated task object }
```

**Delete Task**
```http
DELETE /api/v1/users/{user_id}/tasks/{task_id}
Authorization: Bearer <token>

Response: 204 No Content
```

**Complete Task**
```http
PATCH /api/v1/users/{user_id}/tasks/{task_id}/complete
Authorization: Bearer <token>
Content-Type: application/json

{
  "complete": true
}

Response: 200 OK
{ task with status="completed" and completed_at timestamp }
```

## Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://user:password@host:5432/todo_db
DATABASE_POOL_SIZE=5
DATABASE_POOL_TIMEOUT=30
JWT_SECRET_KEY=your-super-secret-key-change-this
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=development
LOG_LEVEL=INFO
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

## Deployment

### Backend Deployment (Railway/Render)

1. **Prepare for deployment:**
   - Update production environment variables
   - Set strong JWT_SECRET_KEY
   - Configure ALLOWED_ORIGINS for your frontend domain

2. **Deploy to Railway.app:**
   - Connect your GitHub repository
   - Select the `backend` directory
   - Set environment variables
   - Deploy

3. **Or deploy to Render.com:**
   - Create new Web Service
   - Connect GitHub repository
   - Select Python environment
   - Set environment variables and deploy

### Frontend Deployment (Vercel)

1. **Deploy to Vercel:**
   - Push code to GitHub
   - Import project in Vercel Dashboard
   - Set environment variables (NEXT_PUBLIC_API_BASE_URL pointing to your backend)
   - Deploy

2. **Or deploy to Netlify:**
   - Connect GitHub repository
   - Set build command: `pnpm build`
   - Set publish directory: `.next`
   - Deploy

## Development Workflow

### Creating a New Feature

1. Update specifications in `@specs/` directory
2. Generate implementation plan
3. Break down into atomic tasks
4. Implement following the plan
5. Write tests
6. Submit for review

### Running Tests

**Backend:**
```bash
pytest app/tests/ -v
```

**Frontend:**
```bash
pnpm test  # or npm run test
```

### Code Quality

**Backend:**
```bash
flake8 app/
black app/
```

**Frontend:**
```bash
eslint . --ext .ts,.tsx
prettier --check .
```

## Troubleshooting

### Database Connection Issues
- Verify DATABASE_URL is correct
- Check if PostgreSQL/Neon is accessible
- Try expanding connection timeout: `DATABASE_POOL_TIMEOUT=60`

### Authentication Issues
- Ensure JWT_SECRET_KEY is set in backend
- Check token expiration time
- Verify CORS settings for frontend origin

### API Not Accessible from Frontend
- Check ALLOWED_ORIGINS in backend .env
- Verify NEXT_PUBLIC_API_BASE_URL is correct
- Check browser console for CORS errors

## Security Considerations

1. **Never commit .env files** - Use .env.example as template
2. **Change JWT_SECRET_KEY** for production
3. **Use HTTPS** in production
4. **Enable database encryption** for sensitive data
5. **Implement rate limiting** for API endpoints
6. **Keep dependencies updated** - Run `pip install --upgrade pip` and `pnpm update`

## Contributing

Follow the Spec-Driven Development methodology:
1. Create/update specifications
2. Generate implementation plans
3. Implement according to specs
4. Test thoroughly
5. Submit changes

## License

This project is part of Hackathon II - Spec-Driven Development.

## Support

For issues or questions:
1. Check the specifications in `@specs/` directory
2. Review API documentation
3. Check logs for error details
4. Refer to environment variables documentation

## Deployment Links

- **Backend API**: [To be deployed]
- **Frontend App**: [To be deployed]
- **Demo Video**: [To be added]

## Success Checklist for Phase II

- [x] Complete full-stack application architecture
- [x] User authentication implementation
- [x] Task CRUD operations
- [x] Responsive user interface
- [x] Security best practices
- [x] API documentation
- [ ] Deploy backend
- [ ] Deploy frontend
- [ ] Record demo video
- [ ] Submit GitHub repository URL
- [ ] Submit deployment links
- [ ] Submit demo video link

---

**Phase II Completion Status**: In Progress ✓  
**Last Updated**: February 2026  
**Spec-Driven Development**: Yes ✓
