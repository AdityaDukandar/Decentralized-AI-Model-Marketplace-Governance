FROM python:3.10-slim

# Make backend the Python package root
WORKDIR /app/backend

# Copy whole repo into container at /app (so /app/backend exists)
COPY . /app

# Install requirements using full path
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Ensure Python can import backend modules by default
ENV PYTHONPATH=/app/backend

EXPOSE 8000

# Run uvicorn from the backend package
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]
