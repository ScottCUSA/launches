# Start from a base image
FROM python:3.12-alpine as runtime

# Set a working directory
WORKDIR /app

# Copy the project files into the working directory
COPY . .

# Install dependencies
RUN pip install -r requirements.lock

# Set the command to run your application
CMD ["launches", "--service-mode"]
