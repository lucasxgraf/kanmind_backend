# Kanmind Backend

REST API backend for the Kanmind Kanban board application, built with Django and Django REST Framework.

## Tech Stack

- Python 3.x
- Django 6.0
- Django REST Framework 3.17
- SQLite (development database)
- Token-based authentication

## Project Structure

```
kanmind_backend/
├── core/               # Project settings and root URL configuration
├── auth_app/           # User registration, login, logout, email check
│   └── api/            # Serializers, views, URLs
├── boards_app/         # Kanban board management
│   └── api/            # Serializers, views, URLs, permissions
├── tasks_app/          # Task and comment management
│   └── api/            # Serializers, views, URLs, permissions
├── manage.py
├── requirements.txt
└── .gitignore
```

## Getting Started

### 1. Clone the repository

```bash
git clone <repository-url>
cd kanmind_backend
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate      # macOS / Linux
.venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
```

### 5. Apply database migrations

```bash
python manage.py migrate
```

### 6. Create a superuser (optional, for Django Admin)

```bash
python manage.py createsuperuser
```

### 7. Start the development server

```bash
python manage.py runserver
```

The API is available at `http://127.0.0.1:8000/api/`.  
The Django Admin is available at `http://127.0.0.1:8000/admin/`.

## API Endpoints

All endpoints except registration and login require a token in the `Authorization` header:

```
Authorization: Token <your-token>
```

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/registration/` | Register a new user |
| POST | `/api/login/` | Log in and receive a token |
| POST | `/api/logout/` | Invalidate the current token |
| GET | `/api/email-check/?email=<email>` | Look up a user by email |
| GET/POST | `/api/boards/` | List boards or create a new one |
| GET/PATCH/DELETE | `/api/boards/{id}/` | Retrieve, update, or delete a board |
| GET/POST | `/api/tasks/` | List tasks or create a new one |
| GET/PATCH/DELETE | `/api/tasks/{id}/` | Retrieve, update, or delete a task |
| GET | `/api/tasks/assigned-to-me/` | Tasks assigned to the current user |
| GET | `/api/tasks/reviewing/` | Tasks where the current user is reviewer |
| GET/POST | `/api/tasks/{id}/comments/` | List or add comments on a task |
| GET/DELETE | `/api/tasks/{id}/comments/{comment_id}/` | Retrieve or delete a comment |