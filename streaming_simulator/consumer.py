import grpc
import time
from confluent_kafka import Consumer, KafkaError
import numpy as np
import sys

# We need to make sure the inference_service package is on the Python path
# This is required to run this script as a module from the root directory
from inference_service.protos import inference_pb2
from inference_service.protos import inference_pb2_grpc

KAFKA_TOPIC = "video-frames"
GRPC_SERVER = "localhost:50051"
RUN_DURATION_SECONDS = 30

# --- NEW Confluent Kafka Configuration ---
kafka_config = {
    'bootstrap.servers': 'pkc-56d1g.eastus.azure.confluent.cloud:9092',
    'sasl.mechanism': 'PLAIN',
    'security.protocol': 'SASL_SSL',
    'sasl.username': 'XECLJIIHJBRRUSBG',
    'sasl.password': 'cflt69Y0dOzzy5uQOtHqNJuOfe05cFuC0I9uAv0fSSMurD8sJPFXYrOEGUAysGVA',
    'group.id': 'my-video-consumer-group',  # Consumer group ID
    'auto.offset.reset': 'latest' # Start from the latest message
}
# --- END CONFIG ---

def main():
    print("Starting consumer with Confluent client...")
    # Create Consumer instance
    consumer = Consumer(kafka_config)
    # Subscribe to the topic
    consumer.subscribe([KAFKA_TOPIC])

    # Setup gRPC client
    channel = grpc.insecure_channel(GRPC_SERVER)
    stub = inference_pb2_grpc.InferenceServiceStub(channel)

    print(f"Consumer will run for {RUN_DURATION_SECONDS} seconds...")
    latencies = []
    frame_count = 0
    start_time = time.time()

    try:
        while time.time() - start_time < RUN_DURATION_SECONDS:
            # The poll() method is the core of the consumer loop
            msg = consumer.poll(timeout=1.0)

            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition event
                    print('Reached end of topic partition.')
                else:
                    print(f'Error: {msg.error()}')
                continue

            # We have a valid message
            frame_count += 1
            inference_start_time = time.time()

            request = inference_pb2.ImageRequest(image_data=msg.value())
            response = stub.Predict(request)

            latency_ms = (time.time() - inference_start_time) * 1000
            latencies.append(latency_ms)

            print(f"Frame {frame_count:04d}: Prediction='{response.prediction}', Latency={latency_ms:.2f} ms")

    except KeyboardInterrupt:
        print("Stopping consumer manually.")
    finally:
        # Close down consumer to commit final offsets.
        consumer.close()
        
        # --- Print Final Performance Metrics ---
        total_time = time.time() - start_time
        if frame_count > 0:
            avg_latency = np.mean(latencies)
            # Adjust throughput calculation for the actual run duration
            throughput = frame_count / (time.time() - start_time)
            
            print("\n--- 📊 Performance Summary ---")
            print(f"Total frames processed: {frame_count}")
            print(f"Total run time: {total_time:.2f} seconds")
            print(f"Average latency per frame: {avg_latency:.2f} ms")
            print(f"Average throughput: {throughput:.2f} FPS (Frames Per Second)")
            print("-----------------------------\n")
        else:
            print("No frames were processed.")

if __name__ == "__main__":
    main()