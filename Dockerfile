# Use Python 3.12 slim variant (lighter base image)
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies required for Rust, PostgreSQL, and package compilation
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Rust and Cargo (needed for compiling `pydantic_core` and `httptools`)
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Upgrade pip to avoid dependency issues
RUN pip install --upgrade pip setuptools wheel

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application into the container
COPY . .

# Expose the application port
EXPOSE 8000

# Run the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
