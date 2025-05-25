# Start from a base image
FROM ghcr.io/astral-sh/uv:debian-slim as runtime

# Set a working directory
WORKDIR /app

# Copy the project files into the working directory
COPY . .

# Install dependencies
RUN uv sync --locked --all-extras

# Set the command to run your application
CMD ["uv", "run", "launches", "--service"]
