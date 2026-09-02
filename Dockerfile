FROM python:3.12-slim

WORKDIR /code

# Install dependencies first, so this layer is cached unless requirements change
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Run migrations, then start the server.
# $PORT is provided by the hosting platform.
CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}