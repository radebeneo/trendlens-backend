# TrendLens Backend

Backend API for TrendLens - The Zeitgeist of the Internet.

## Tech Stack
- **FastAPI**: Modern, fast (high-performance), web framework for building APIs.
- **SQLAlchemy**: Python SQL toolkit and Object Relational Mapper.
- **PostgreSQL**: Primary database.
- **Pydantic**: Data validation and settings management using Python type annotations.

## Getting Started

### 1. Prerequisites
- Python 3.9+
- PostgreSQL

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the root directory:
```
DATABASE_URL=postgresql://user:password@localhost/trendlens
```
*(Default is `postgresql://postgres:postgres@localhost/trendlens`)*

### 4. Run the Application
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.
Documentation (Swagger UI) is at `http://127.0.0.1:8000/docs`.

## Project Structure
- `app/main.py`: Entry point and API routes.
- `app/models.py`: SQLAlchemy database models.
- `app/schemas.py`: Pydantic models for request/response validation.
- `app/database.py`: Database connection and session management.
