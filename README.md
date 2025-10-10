

# Real-Time ML Streaming Pipeline with Streamlit Controller

This project demonstrates a complete, end-to-end MLOps pipeline for real-time image classification. It ingests a video stream, performs inference using a PyTorch model served over a high-performance gRPC API, and provides a Streamlit-based web UI to control and monitor the entire process.

-----

## 🏛️ Architecture

The pipeline consists of several decoupled components that communicate via a Kafka message broker. A Streamlit dashboard acts as a central control panel.

```mermaid
graph TD
    subgraph "Control Layer"
        F[🎈 Streamlit UI]
    end

    subgraph "Data Plane"
        A[Video Source] --> B(🐍 Producer);
        B -- Video Frames --> C{🌊 Kafka / Confluent Cloud};
        C -- Video Frames --> D(🐍 Consumer);
        D -- gRPC Request --> E[🚀 gRPC Inference Server <br> (🔥 PyTorch Model)];
        E -- Prediction --> D;
    end

    F -- Manages --> B;
    F -- Manages --> D;
    F -- Manages --> E;
```

-----

## ✨ Features

  * **High-Performance Inference**: A PyTorch ResNet18 model is served over gRPC for low-latency predictions.
  * **Real-Time Data Streaming**: Apache Kafka (using Confluent Cloud) handles high-throughput, real-time data ingestion from a video source.
  * **Containerized Service**: The inference server is containerized with Docker for portability, scalability, and reproducible deployments.
  * **Interactive Control Panel**: A Streamlit dashboard allows for starting, stopping, and monitoring all pipeline components from a single web interface, eliminating the need to manage multiple terminals.
  * **Decoupled Components**: The producer, consumer, and server are independent, allowing them to be scaled or updated separately.

-----

## 🛠️ Tech Stack

  * **Python**: Core programming language.
  * **PyTorch**: For the image classification model.
  * **gRPC**: For the high-performance inference API.
  * **Apache Kafka (Confluent Cloud)**: For the real-time message broker.
  * **Streamlit**: For the interactive web-based control panel.
  * **Docker & Docker Compose**: For containerization and service orchestration.
  * **OpenCV**: For video and image processing.

-----

## Prerequisites

Before you begin, ensure you have the following installed:

  * Python 3.9+
  * `pip` (Python package installer)
  * Docker Desktop

-----

## ⚙️ Setup & Installation

1.  **Clone the Repository**
    ```bash
    git clone <your-repo-url>
    cd ml-streaming-pipeline
    ```
2.  **Create a Virtual Environment (Recommended)**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```
3.  **Install Dependencies**
    This project contains multiple `requirements.txt` files. To run the Streamlit app, install the dependencies from the root `requirements.txt` file (if you created one based on our conversation) or install from both service-specific files:
    ```bash
    pip install -r requirements.txt
    ```

-----

## 🔧 Configuration

This project requires credentials to connect to a Kafka cluster (like Confluent Cloud).

1.  **Sign up** for a free Confluent Cloud account and create a cluster.
2.  **Create an API key and secret**.
3.  Open the `streaming_simulator/producer.py` and `streaming_simulator/consumer.py` files.
4.  Update the `kafka_config` dictionary in both files with your **Bootstrap Server**, **API Key**, and **API Secret**.

-----

## 🚀 Usage

You can run this pipeline in two ways:

### Method 1: Using the Streamlit Controller (Recommended)

This method provides a user-friendly web interface to manage all components.

1.  **Generate gRPC Code**
    If you haven't already, run this command from the root directory to generate the necessary gRPC Python files:
    ```bash
    python -m grpc_tools.protoc -I=inference_service/protos --python_out=. --grpc_python_out=. inference_service/protos/inference.proto
    ```
2.  **Launch the Streamlit App**
    ```bash
    streamlit run streamlit_app.py
    ```
3.  **Control the Pipeline**
      * Your browser will open with the dashboard.
      * Click "Start Server", then "Start Consumer", then "Start Producer".
      * Monitor the logs in the text boxes for each component.
      * Click "Stop All Services" when you're finished.

### Method 2: Using Docker and Manual Scripts

This method runs the inference server in a Docker container and the streaming clients locally.

1.  **Start the Services**
    This command will build the Docker image for the inference server and start it.
    ```bash
    docker-compose up --build -d
    ```
2.  **Run the Consumer**
    Open a new terminal and run the consumer module:
    ```bash
    python -m streaming_simulator.consumer
    ```
3.  **Run the Producer**
    Open a third terminal and run the producer script:
    ```bash
    python streaming_simulator/producer.py
    ```
4.  **Shut Down**
    When you're finished, stop and remove the Docker containers:
    ```bash
    docker-compose down
    ```

-----

## 📂 Folder Structure

```
.
├── inference_service/    # gRPC server and model logic
├── streaming_simulator/  # Kafka producer and consumer scripts
├── streamlit_app.py      # The main Streamlit controller UI
├── Dockerfile            # Docker instructions for the inference service
└── docker-compose.yml    # Docker Compose file for orchestration
```