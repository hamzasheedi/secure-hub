# SecureVault Project Startup Guide

## Prerequisites

- Python 3.11+
- Node.js 18+ (if using frontend)
- PostgreSQL 12+
- Git

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd SecureVault
```

### 2. Set Up Environment

Copy the example environment file and customize it:

```bash
cp .env.example .env
```

Edit the `.env` file to match your local configuration.

### 3. Backend Setup

#### Create a Virtual Environment

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Install Dependencies

```bash
pip install -r requirements.txt
```

#### Run Database Migrations

```bash
alembic upgrade head
```

#### Start the Backend Server

```bash
uvicorn src.main:app --reload
```

The backend API will be available at `http://localhost:8000`

### 4. Frontend Setup (if applicable)

#### Navigate to Frontend Directory

```bash
cd frontend  # From project root
```

#### Install Dependencies

```bash
npm install
```

#### Copy Environment File

```bash
cp .env.example .env.local
```

#### Start the Development Server

```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

### 5. Create Admin Account

Before using the application, create an admin account:

```bash
cd ..  # From backend directory, back to project root
python create_admin.py
```

Follow the prompts to create your admin account.

### 6. Running the Application

#### Backend Only

If you're only using the API:

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn src.main:app --reload
```

#### Complete Application (Backend + Frontend)

1. Start the backend server as described above
2. In a separate terminal, start the frontend as described above

### 7. API Documentation

Once the backend is running, API documentation is available at:
- `http://localhost:8000/docs` (Swagger UI)
- `http://localhost:8000/redoc` (ReDoc)

### 8. Testing

#### Backend Tests

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
pytest
```

#### Frontend Tests

```bash
cd frontend
npm test
```

### 9. Production Deployment

For production deployment:

1. Set `DEBUG=False` in your environment
2. Use a production-grade database
3. Use a WSGI/ASGI server like Gunicorn or Hypercorn
4. Set up a reverse proxy like Nginx
5. Ensure all security configurations are properly set

Example production startup for backend:
```bash
cd backend
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 10. Troubleshooting

#### Common Issues

1. **Port Already in Use**: Change the port in your `.env` file
2. **Database Connection Error**: Verify your `DATABASE_URL` in `.env`
3. **Module Import Errors**: Ensure you've installed all dependencies
4. **Permission Errors**: Check file permissions, especially for storage directories

#### Resetting the Application

To reset the application state:
1. Drop and recreate the database
2. Run migrations again: `alembic upgrade head`
3. Recreate the admin account

### 11. Security Notes

- Change all default passwords and secret keys in `.env`
- Use HTTPS in production
- Regularly update dependencies
- Monitor logs for suspicious activity
- Follow the principle of least privilege for user accounts