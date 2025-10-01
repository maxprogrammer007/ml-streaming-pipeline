import grpc
import time
from kafka import KafkaConsumer
import numpy as np
import sys

# This line allows us to import the gRPC files from the other directory
sys.path.append('..\\inference_service')
import protos.inference_pb2 as inference_pb2
import protos.inference_pb2_grpc as inference_pb2_grpc


KAFKA_TOPIC = "video-frames"
KAFKA_BROKER = "localhost:9092"
GRPC_SERVER = "localhost:50051"
RUN_DURATION_SECONDS = 30 # How long to run the test

def main():
    print("Starting consumer...")
    
    # Setup Kafka Consumer to receive messages
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        auto_offset_reset='latest', # Start reading from the newest message
        client_id="video-consumer"
    )

    # Setup gRPC client to send requests to the inference server
    channel = grpc.insecure_channel(GRPC_SERVER)
    stub = inference_pb2_grpc.InferenceServiceStub(channel)

    print(f"Consumer will run for {RUN_DURATION_SECONDS} seconds...")
    latencies = []
    frame_count = 0
    start_time = time.time()

    try:
        for message in consumer:
            current_time = time.time()
            if current_time - start_time > RUN_DURATION_SECONDS:
                break # Stop after the specified duration

            frame_count += 1
            
            # --- Performance Measurement Start ---
            inference_start_time = time.time()

            request = inference_pb2.ImageRequest(image_data=message.value)
            response = stub.Predict(request)

            latency_ms = (time.time() - inference_start_time) * 1000 # Convert to milliseconds
            latencies.append(latency_ms)
            # --- Performance Measurement End ---

            print(f"Frame {frame_count:04d}: Prediction='{response.prediction}', Latency={latency_ms:.2f} ms")

    except KeyboardInterrupt:
        print("Stopping consumer manually.")
    finally:
        # --- Print Final Performance Metrics ---
        total_time = time.time() - start_time
        if frame_count > 0:
            avg_latency = np.mean(latencies)
            throughput = frame_count / total_time
            
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