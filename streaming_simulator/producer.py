import cv2
import time
from kafka import KafkaProducer

KAFKA_TOPIC = "video-frames"
KAFKA_BROKER = "localhost:9092"
VIDEO_SOURCE = "test_video.mp4" # Make sure this file exists in this directory

def main():
    print("Starting producer...")
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        client_id="video-producer"
    )

    cap = cv2.VideoCapture(VIDEO_SOURCE)
    if not cap.isOpened():
        print(f"Error: Could not open video source at {VIDEO_SOURCE}")
        return
        
    print(f"Reading video from '{VIDEO_SOURCE}' and sending frames to topic '{KAFKA_TOPIC}'...")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            # If the video ends, loop back to the beginning
            print("Video finished. Restarting from the beginning...")
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        # Encode the frame as a JPEG image
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            print("Error: Failed to encode frame.")
            continue
        
        # Send the encoded frame to the Kafka topic
        producer.send(KAFKA_TOPIC, buffer.tobytes())
        
        # Simulate a real-world camera's frame rate (~30 FPS)
        time.sleep(1/30) 

    cap.release()
    print("Producer finished.")

if __name__ == "__main__":
    main()