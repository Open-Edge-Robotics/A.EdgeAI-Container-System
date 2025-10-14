# Robot Platform API

A FastAPI-based REST API for managing workspaces, projects, clusters, and platform services.


## Design (Figma)

- [Figma](https://www.figma.com/design/4OvbXHcCGQgjF9XLwsKRVQ/Griffin-Robot-Platform?node-id=0-1&p=f&m=dev)

## Features

- User authentication and authorization
- Workspace management
- Project management within workspaces
- Cluster management within projects
- Platform service management
- Role-based access control

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- MongoDB 4.4 or higher

## Installation

1. Clone the repository:
```bash
http://git.etri.dev/edge/rosplatform.git
cd rosplatform
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with the following variables:
```
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=robotplatform
MONGODB_USER=your_username  # Optional
MONGODB_PASSWORD=your_password  # Optional
SECRET_KEY=your-secret-key-here
```

5. Initialize MongoDB:
```bash
python scripts/init_db.py
```

## Running the Application

1. Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

2. Access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication
- POST `/token` - Get access token

### Users
- POST `/users/` - Create new user

### Workspaces
- POST `/workspaces/` - Create workspace
- GET `/workspaces/` - List workspaces
- GET `/workspaces/{workspace_id}` - Get workspace
- PUT `/workspaces/{workspace_id}` - Update workspace
- DELETE `/workspaces/{workspace_id}` - Delete workspace

### Projects
- POST `/projects/` - Create project
- GET `/projects/` - List projects
- GET `/projects/{project_id}` - Get project
- PUT `/projects/{project_id}` - Update project
- DELETE `/projects/{project_id}` - Delete project

### Clusters
- POST `/clusters/` - Create cluster
- GET `/clusters/` - List clusters
- GET `/clusters/{cluster_id}` - Get cluster
- PUT `/clusters/{cluster_id}` - Update cluster
- DELETE `/clusters/{cluster_id}` - Delete cluster

### Platform Services
- GET `/platform/services/` - List services
- POST `/platform/services/` - Create service
- GET `/platform/services/{name}` - Get service
- PUT `/platform/services/{name}` - Update service
- DELETE `/platform/services/{name}` - Delete service

## Security

- All endpoints except `/token` and `/users/` require authentication
- Admin-only endpoints are protected with role-based access control
- Passwords are hashed using bcrypt
- JWT tokens are used for authentication

## Database

The application uses MongoDB as the database. To configure the database:

1. Install MongoDB on your system
2. Update the `MONGODB_URL` and `DATABASE_NAME` in the `.env` file
3. Run the initialization script to create collections and indexes:
   ```bash
   python scripts/init_db.py
   ```

## Development

To run tests (when implemented):
```bash
pytest
```

## Documentation Files

### README.md
This is the main documentation file for the project. It contains:
- Project overview and features
- Installation instructions
- API endpoint documentation
- Security information
- Database configuration
- Development guidelines

### .gitignore
Configuration file that specifies intentionally untracked files that Git should ignore. It includes:
- Python bytecode files
- Virtual environment directories
- IDE configuration files
- Build and distribution directories
- Environment files
- Test coverage reports
- Database files
- Log files

## License

zero license