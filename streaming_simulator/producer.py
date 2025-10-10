import cv2
import time
from confluent_kafka import Producer
import socket

def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result. """
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        # This can be very verbose, so it's commented out.
        # print(f'Message delivered to {msg.topic()} [{msg.partition()}]')
        pass

# --- Confluent Kafka Configuration ---
kafka_config = {
    'bootstrap.servers': 'pkc-56d1g.eastus.azure.confluent.cloud:9092',
    'sasl.mechanism': 'PLAIN',
    'security.protocol': 'SASL_SSL',
    'sasl.username': 'XECLJIIHJBRRUSBG', 
    'sasl.password': 'cflt69Y0dOzzy5uQOtHqNJuOfe05cFuC0I9uAv0fSSMurD8sJPFXYrOEGUAysGVA', 
    'client.id': socket.gethostname()
}
# --- END CONFIG ---

KAFKA_TOPIC = "video-frames"
VIDEO_SOURCE = "C:\\Users\\abhin\\OneDrive\\Documents\\GitHub\\ml-streaming-pipeline\\streaming_simulator\\test_video.mp4"

def main():
    print("Starting producer with Confluent client...")
    producer = Producer(kafka_config)

    cap = cv2.VideoCapture(VIDEO_SOURCE)
    if not cap.isOpened():
        print(f"Error: Could not open video source at {VIDEO_SOURCE}")
        return
        
    print(f"Reading video from '{VIDEO_SOURCE}' and sending frames to topic '{KAFKA_TOPIC}'...")
    
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Video finished. Restarting from the beginning...")
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            print("Error: Failed to encode frame.")
            continue
        
        producer.poll(0)
        
        producer.produce(KAFKA_TOPIC, buffer.tobytes(), callback=delivery_report)
        
        frame_count += 1
        if frame_count % 100 == 0:
            print(f"{frame_count} frames sent...")
        
        time.sleep(1/30)

    print("Flushing messages...")
    producer.flush()
    print("Producer finished.")

if __name__ == "__main__":
    main()