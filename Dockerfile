FROM python:3.11-slim

ENV PYTHONPATH="${PYTHONPATH}:/app"
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Debugging message during build
RUN echo "Dependencies installed"

COPY . .

EXPOSE 8001

# Command to run the storage application
CMD ["uvicorn", "storage_api.storage_app:storage_app", "--host", "0.0.0.0", "--port", "8001"]

# Debugging message during container start
RUN echo "Hello world from storage_api container"


