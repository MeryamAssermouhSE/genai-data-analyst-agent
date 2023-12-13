# Use a specific Python version
FROM python:3.11

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Set the working directory
ENV APP_HOME /app
WORKDIR $APP_HOME

# Copy only the requirements file to leverage Docker cache
COPY requirements.txt .

# Install production dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy local code to the container image
COPY . .

# Expose the port (optional, as Cloud Run handles this automatically)
EXPOSE 8080

# Run the Streamlit application
ENTRYPOINT ["streamlit", "run", "--server.port", "8080", "--server.enableCORS", "false", "app.py"]
