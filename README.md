# OmniHR backend assignment

This is the documentation for installation requirements, spinning up API server and running unit tests.

## Installation requirements

1. Python
2. Docker
3. Asdf (optional)

## Usage

1. Firstly, initialize and activate virtual environment in the current root project directory
```bash
python -m venv venv
source venv/bin/activate
```

2. Install required Python dependencies:
```bash
pip install -r requirements.txt
```

3. Generate mock data, it generates around 1 million records so please be patient:
```bash
python scripts/generate_mock_data.py
```

4. Spin up docker compose stack:
```bash
docker-compose -f docker/development/docker-compose.yml up --build -d
```

5. Run unit tests:
```bash
pytest
```

6. Perform some sample queries:
```bash
curl http://localhost:8000/search?query=John&status=active&status=terminated
```

7. Documentation links:
- http://localhost:8000/redoc
- http://localhost:8000/docs
