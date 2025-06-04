# Use official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /project

# Set environment variables
ENV GITHUB_SECRET=e7c64fc5-d12a-4ccc-ad3c-a4c809be0f09
ENV MONGO_USERNAME=anish2272002
ENV MONGO_PASSWORD=Anish@2272002
ENV PYTHONUNBUFFERED=1


# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Run the Flask app
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app","--capture-output", "--log-level=debug"]