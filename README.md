# Full Stack Application

This is a full-stack application with a React frontend and Django backend.

## Prerequisites

- Node.js (v16 or higher)
- Python (v3.8 or higher)
- npm (comes with Node.js)
- pip (Python package manager)

## Setup

1. Install all dependencies:
```bash
npm run install:all
```

This will install:
- Root dependencies
- Frontend dependencies
- Backend dependencies

## Development

To run both frontend and backend in development mode:

```bash
npm start
```

This will start:
- Frontend development server on http://localhost:5173
- Backend development server on http://localhost:8000

The frontend is configured to proxy API requests to the backend automatically.

## Building for Production

To build the frontend:

```bash
npm run build
```

The built files will be in the `frontend/dist` directory.

## Testing

To run all tests:

```bash
npm test
```

This will run:
- Frontend tests
- Backend tests

## API Documentation

The API documentation is available at:
- Swagger UI: http://localhost:8000/api/swagger/
- ReDoc: http://localhost:8000/api/redoc/

## Project Structure

```
.
├── frontend/          # React frontend
├── backend/           # Django backend
│   ├── api/          # API endpoints
│   ├── core/         # Django project settings
│   ├── security/     # Authentication and users
│   └── wallets/      # Wallet functionality
└── docs/             # Documentation
```