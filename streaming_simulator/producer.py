#!/usr/bin/env python3
"""
Kafka/Redpanda producer that simulates streaming image data.
"""

import logging
import time
import json
from typing import Optional

# TODO: Import Kafka client
# from kafka import KafkaProducer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImageStreamProducer:
    """
    Produces simulated image data to a Kafka/Redpanda topic.
    """
    
    def __init__(self, bootstrap_servers: str, topic: str):
        """
        Initialize the producer.
        
        Args:
            bootstrap_servers: Kafka/Redpanda bootstrap servers
            topic: Topic to produce messages to
        """
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.producer = None
        logger.info(f"Initializing producer for topic: {topic}")
    
    def connect(self):
        """Connect to Kafka/Redpanda."""
        # TODO: Initialize KafkaProducer
        # self.producer = KafkaProducer(
        #     bootstrap_servers=self.bootstrap_servers,
        #     value_serializer=lambda v: json.dumps(v).encode('utf-8')
        # )
        logger.info("Producer connected")
    
    def produce_message(self, image_data: bytes, metadata: Optional[dict] = None):
        """
        Produce a message to the topic.
        
        Args:
            image_data: Raw image bytes
            metadata: Optional metadata dictionary
        """
        message = {
            'image': image_data.hex() if isinstance(image_data, bytes) else image_data,
            'timestamp': time.time(),
            'metadata': metadata or {}
        }
        # TODO: Send message
        # self.producer.send(self.topic, value=message)
        logger.info(f"Produced message to {self.topic}")
    
    def close(self):
        """Close the producer connection."""
        if self.producer:
            # self.producer.flush()
            # self.producer.close()
            logger.info("Producer closed")


def main():
    """Main function to run the producer."""
    producer = ImageStreamProducer(
        bootstrap_servers='localhost:9092',
        topic='image-stream'
    )
    producer.connect()
    
    try:
        while True:
            # TODO: Generate or load sample images
            producer.produce_message(b'sample_image_data')
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down producer")
    finally:
        producer.close()


if __name__ == '__main__':
    main()
