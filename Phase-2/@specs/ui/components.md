# UI Components Specification

## Overview
This document defines the reusable UI components for the Todo application. Each component specification describes the functionality, user interactions, and behaviors without focusing on visual styling details.

## Task Item Component

### Purpose
Display a single task with its details and provide action controls.

### Properties/Props
- `task`: Object containing task data (id, title, description, status, priority, due_date, etc.)
- `onEdit`: Function called when edit button is clicked
- `onDelete`: Function called when delete button is clicked
- `onToggleComplete`: Function called when completion status changes
- `isEditable`: Boolean indicating if user can edit this task

### Functionality
- Display task title prominently
- Show task description if available
- Indicate task status (active/completed) visually
- Show task priority level
- Display due date if set
- Show creation/update timestamps
- Provide edit button
- Provide delete button
- Provide completion toggle (checkbox or button)

### User Interactions
- Clicking edit button calls onEdit callback with task data
- Clicking delete button calls onDelete callback with task ID
- Clicking completion toggle calls onToggleComplete with task ID and new status
- Hover effects on action buttons
- Keyboard navigation support for action buttons

### Behavior Requirements
- Reflect task status changes immediately in UI
- Show visual indication when task is completed
- Disable actions if task is not editable
- Show confirmation for destructive actions (deletion)
- Update appearance based on task priority

### Error Handling
- If task data is invalid, show placeholder or error state
- If action fails, revert UI and show error message
- Handle network errors gracefully during action execution

## Task Form Component

### Purpose
Provide interface for creating or editing tasks.

### Properties/Props
- `initialData`: Object with task data for editing (empty for creation)
- `onSubmit`: Function called when form is submitted
- `onCancel`: Function called when form is cancelled
- `submitLabel`: Label for submit button (e.g., "Create Task" or "Update Task")

### Functionality
- Title input field (required, 1-255 characters)
- Description textarea (optional, max 1000 characters)
- Status selection (active/completed)
- Priority selection (low/medium/high)
- Due date picker (optional)
- Submit button
- Cancel button
- Form validation indicators

### User Interactions
- Submit button validates form and calls onSubmit with task data
- Cancel button calls onCancel without saving
- Real-time validation feedback
- Auto-focus on first field
- Keyboard submission support (Enter key)

### Behavior Requirements
- Pre-populate fields when editing existing task
- Validate inputs before submission
- Show validation errors near relevant fields
- Prevent submission with invalid data
- Clear form after successful submission (when creating)

### Error Handling
- Display validation errors for invalid inputs
- Show submission errors if API call fails
- Preserve user input if submission fails
- Handle network errors gracefully

## Navigation Component

### Purpose
Provide consistent navigation across all application pages.

### Properties/Props
- `user`: Object containing authenticated user data (optional, null if not authenticated)
- `currentPage`: String indicating current page for active link highlighting
- `onLogout`: Function called when logout is triggered

### Functionality
- Logo/branding display
- Navigation links (Dashboard, Profile, etc.)
- User profile dropdown when authenticated
- Login/Signup links when not authenticated
- Logout button when authenticated

### User Interactions
- Clicking navigation links changes page
- Clicking user profile shows dropdown menu
- Clicking logout calls onLogout function
- Active page highlighted in navigation
- Dropdown menu closes when clicking elsewhere

### Behavior Requirements
- Show appropriate links based on authentication state
- Highlight current page in navigation
- Maintain consistent appearance across pages
- Collapse on mobile screens if needed

### Error Handling
- If user data is unavailable, show loading state
- If logout fails, show error message and keep session active

## Auth Guard Component

### Purpose
Protect routes that require authentication and redirect unauthenticated users.

### Properties/Props
- `children`: React node(s) to render if user is authenticated
- `fallbackUrl`: URL to redirect to if user is not authenticated (default: '/login')

### Functionality
- Check authentication status on mount
- Verify session validity via Better Auth
- Conditionally render children based on authentication
- Redirect to fallback URL if not authenticated

### User Interactions
- Automatically redirects unauthenticated users
- Preserves intended destination for post-authentication redirect
- Handles session expiration during navigation

### Behavior Requirements
- Check authentication state immediately on component mount
- Subscribe to authentication state changes
- Update rendering when authentication status changes
- Preserve original navigation intent for redirect after login

### Error Handling
- If authentication check fails, treat as unauthenticated
- If session is invalid/expired, redirect to login
- Handle network errors during authentication verification
- Gracefully degrade if Better Auth is unavailable

### Conditional Rendering Logic
- If authenticated: Render children components
- If unauthenticated: Redirect to fallback URL
- If checking status: Show loading indicator (optional)
- If error occurs: Redirect to fallback URL with error parameter

### Integration Points
- Works with Next.js App Router for route protection
- Integrates with Better Auth client-side session management
- Maintains user experience during authentication state transitions
- Preserves URL parameters and query strings when possible

## Additional Component Considerations

### Loading States
- All components should handle loading states gracefully
- Show appropriate indicators during API calls
- Maintain layout stability during loading

### Error Boundaries
- Components should handle rendering errors gracefully
- Provide fallback UI when child components fail
- Log errors for debugging purposes

### Accessibility
- All components must support keyboard navigation
- Proper ARIA attributes for dynamic content
- Screen reader compatibility
- Focus management during state changes