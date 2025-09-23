# Social Campaign CRM with Attribution Tracking

A FastAPI-based CRM system for managing social media campaigns and tracking attribution.

## Features

- **User Authentication**: JWT-based authentication system
- **Campaign Management**: Create, read, update, and delete campaigns
- **Contact Management**: Manage contacts and associate them with campaigns
- **UTM Parameter Generation**: Automatic generation of UTM parameters for tracking
- **API-First Design**: RESTful API with OpenAPI documentation

## Prerequisites

- Python 3.8+
- PostgreSQL 12+
- pip (Python package manager)

## Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd crm
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   Update the `.env` file with your database credentials and other settings.

5. **Set up the database**
   - Create a new PostgreSQL database
   - Update the `DATABASE_URL` in `.env` with your database connection string
   - Example: `postgresql://username:password@localhost:5432/crm_db`

6. **Initialize the database**
   ```bash
   python -m app.db.init_db
   ```

## Running the Application

Start the development server:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the application is running, you can access:

- **Interactive API docs (Swagger UI)**: http://localhost:8000/docs
- **Alternative API docs (ReDoc)**: http://localhost:8000/redoc

## Project Structure

```
crm/
├── app/
│   ├── api/                  # API routes
│   │   └── v1/               # API version 1
│   │       ├── endpoints/    # API endpoints
│   │       └── api.py        # API router
│   ├── core/                 # Core application configuration
│   ├── db/                   # Database configuration
│   ├── models/               # SQLAlchemy models
│   ├── schemas/              # Pydantic models/schemas
│   └── services/             # Business logic
├── alembic/                  # Database migrations
├── tests/                    # Test files
├── .env                      # Environment variables
├── .env.example              # Example environment variables
├── requirements.txt          # Project dependencies
└── README.md                 # This file
```

## Development

### Creating Migrations

1. Install Alembic:
   ```bash
   pip install alembic
   ```

2. Create a new migration:
   ```bash
   alembic revision --autogenerate -m "Your migration message"
   ```

3. Apply migrations:
   ```bash
   alembic upgrade head
   ```

### Testing

Run tests using pytest:

```bash
pytest
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
