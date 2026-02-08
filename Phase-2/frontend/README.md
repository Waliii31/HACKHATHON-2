# Todo Application Frontend

This is the frontend for the Todo application, built with Next.js and React.

## Tech Stack
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Authentication**: JWT (FastAPI backend)
- **API Client**: Axios with JWT integration

## Features
- User authentication (login/signup)
- Task management (CRUD operations)
- Responsive UI design
- Filter and sort tasks
- Task status management (active/completed)

## Installation

1. Clone the repository
2. Navigate to the frontend directory
3. Install dependencies:
   ```bash
   npm install
   # or
   yarn install
   # or
   pnpm install
   ```

## Environment Variables

Create a `.env.local` file in the frontend directory with the following variables:

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
```

## Running the Application

1. Make sure your environment variables are set
2. Run the development server:
   ```bash
   npm run dev
   # or
   yarn dev
   # or
   pnpm dev
   ```
3. The application will be available at `http://localhost:3000`

## Available Scripts

- `npm run dev` - Start the development server
- `npm run build` - Build the application for production
- `npm run start` - Start the production server
- `npm run lint` - Run ESLint

## Project Structure

```
frontend/
├── app/                 # Next.js App Router pages
│   ├── layout.tsx       # Root layout with navigation
│   ├── page.tsx         # Home page
│   ├── login/page.tsx   # Login page
│   ├── signup/page.tsx  # Signup page
│   └── dashboard/page.tsx # Dashboard page
├── components/          # Reusable UI components
│   ├── navigation.tsx   # Navigation component
│   ├── task-item.tsx    # Task display component
│   └── task-form.tsx    # Task form component
├── contexts/            # React Context providers
│   └── auth-context.tsx # Authentication context
├── lib/                 # Utility functions
│   └── api-client.ts    # API client with JWT handling
├── types/               # TypeScript type definitions
│   ├── task.ts          # Task-related types
│   └── user.ts          # User-related types
└── public/              # Static assets
```

## API Integration

The frontend communicates with the backend API through the API client located in `lib/api-client.ts`. The client automatically attaches JWT tokens to requests and handles authentication errors.
