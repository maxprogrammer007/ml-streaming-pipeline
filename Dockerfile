# --- Stage 1: The "Builder" ---
# This stage prepares all our dependencies and generated code.
FROM python:3.9-slim as builder

WORKDIR /app

# First, install only the tool needed to generate gRPC code.
RUN pip install grpcio-tools

# Copy only the files needed to generate the gRPC stubs.
COPY inference_service/requirements.txt .
COPY inference_service/protos/inference.proto ./protos/inference.proto

# Create empty __init__.py files to ensure Python treats them as packages.
RUN mkdir -p protos
RUN touch protos/__init__.py

# Generate the gRPC Python code inside this stage.
RUN python -m grpc_tools.protoc \
    -I./protos \
    --python_out=. \
    --grpc_python_out=. \
    ./protos/inference.proto

# Now, install all the application dependencies.
RUN pip install --no-cache-dir -r requirements.txt


# --- Stage 2: The Final Production Image ---
# This stage builds the final, lightweight image that will actually run.
FROM python:3.9-slim

WORKDIR /app

# Install grpc_health_probe, a small tool to check if our gRPC server is healthy.
RUN GRPC_HEALTH_PROBE_VERSION=v0.4.15 && \
    wget -qO/bin/grpc_health_probe https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/${GRPC_HEALTH_PROBE_VERSION}/grpc_health_probe-linux-amd64 && \
    chmod +x /bin/grpc_health_probe

# Copy the pre-installed Python libraries from the "builder" stage.
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
# Copy the pre-generated gRPC code from the "builder" stage.
COPY --from=builder /app/protos ./protos

# Finally, copy our application's source code.
COPY inference_service/server.py .

# Tell Docker that the container listens on port 50051.
EXPOSE 50051

# Define a healthcheck to ensure the service is running properly.
HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
  CMD ["/bin/grpc_health_probe", "-addr=:50051"]

# The command that will be executed when the container starts.
CMD ["python", "server.py"]