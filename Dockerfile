# Multi-stage build for inference service
FROM python:3.10-slim as inference-base

WORKDIR /app/inference_service

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY inference_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy inference service code
COPY inference_service/ .

# Generate gRPC code from proto files
RUN python -m grpc_tools.protoc \
    -I./protos \
    --python_out=. \
    --grpc_python_out=. \
    ./protos/inference.proto

# Expose gRPC port
EXPOSE 50051

# Run the server
CMD ["python", "server.py"]
