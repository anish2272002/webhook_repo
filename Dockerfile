# Use official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /project

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Run the Flask app
CMD ["python", "run.py"]
