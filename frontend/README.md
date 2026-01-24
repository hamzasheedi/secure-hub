# SecureVault Frontend

This is the frontend for the SecureVault application, built with Next.js.

## Features

- User authentication (login/register)
- Secure file upload and encryption
- File management (list, download, delete)
- Admin panel for user management
- JWT-based session management
- Responsive design

## Tech Stack

- Next.js 14
- React 18
- Tailwind CSS
- JavaScript

## Getting Started

First, install the dependencies:

```bash
npm install
```

Then, run the development server:

```bash
npm run dev
```

Open [https://securevault-ixu4.onrender.com/](https://securevault-ixu4.onrender.com/) with your browser to see the result (default) or [http://localhost:3000](http://localhost:3000) during local development.

## Environment Variables

Create a `.env.local` file in the root directory with the following:

```env
# For local development
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# For production deployment, use the deployed backend
# NEXT_PUBLIC_API_BASE_URL=https://secure-hub.onrender.com
```

## Project Structure

- `src/app/` - Next.js 14 App Router pages
- `src/components/` - Reusable React components
- `src/contexts/` - React context providers
- `src/services/` - API service functions

## API Integration

The frontend communicates with the SecureVault backend API at `http://localhost:8000` by default. The following endpoints are used:

- Authentication: `/auth/login`, `/auth/register`, `/auth/logout`, `/auth/account`
- Vault operations: `/vault/encrypt`, `/vault/decrypt/{file_id}`, `/vault/files`, `/vault/file/{file_id}`
- Admin operations: `/admin/users`, `/admin/user/{id}/activate`, `/admin/user/{id}/deactivate`

## Security Features

- JWT token handling for authentication
- Secure session management
- Password strength validation
- Role-based access control (user/admin)
- Encrypted file handling

## Running with the Backend

### Local Development

To run the complete SecureVault application locally:

1. First, start the backend server:
   ```bash
   cd ../backend
   uvicorn src.main:app --reload
   ```

2. In a separate terminal, start the frontend:
   ```bash
   npm run dev
   ```

The backend will be available at `http://localhost:8000` and the frontend at `http://localhost:3000` during local development.

### Production Deployment

When deploying the frontend to production (e.g., to Vercel, Netlify, or Render):

1. Set the `NEXT_PUBLIC_API_BASE_URL` environment variable to point to your deployed backend:
   ```
   NEXT_PUBLIC_API_BASE_URL=https://secure-hub.onrender.com
   ```

2. Build and deploy your frontend application.

The frontend will then be available at `https://securevault-ixu4.onrender.com/` (or your custom domain) and will connect to the backend at `https://secure-hub.onrender.com`.

## Development Notes

- The frontend expects the backend to be running at `http://localhost:8000`
- All API calls are handled through the services in `src/services/api.js`
- Authentication tokens are stored in localStorage
- File encryption/decryption happens on the backend