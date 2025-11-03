"""RabbitMQ messaging for agent communication and task queues."""

import os
import json
import pika
from typing import Callable, Any, Optional
from datetime import datetime


class MessagingConfig:
    """RabbitMQ configuration from environment variables."""
    
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
    RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
    RABBITMQ_USER = os.getenv("RABBITMQ_USER", "agent_user")
    RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "rabbitmq_secure_password_change_me")
    RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST", "agent_team")


class MessageBroker:
    """RabbitMQ message broker for agent communication."""
    
    def __init__(self):
        """Initialize RabbitMQ connection."""
        self.config = MessagingConfig()
        self.connection = None
        self.channel = None
        self._connect()
    
    def _connect(self):
        """Establish connection to RabbitMQ."""
        credentials = pika.PlainCredentials(
            self.config.RABBITMQ_USER,
            self.config.RABBITMQ_PASSWORD
        )
        parameters = pika.ConnectionParameters(
            host=self.config.RABBITMQ_HOST,
            port=self.config.RABBITMQ_PORT,
            virtual_host=self.config.RABBITMQ_VHOST,
            credentials=credentials
        )
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
    
    def close(self):
        """Close RabbitMQ connection."""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
    
    # Queue management
    def create_queue(self, queue_name: str, durable: bool = True):
        """Create a queue."""
        self.channel.queue_declare(queue=queue_name, durable=durable)
    
    def delete_queue(self, queue_name: str):
        """Delete a queue."""
        self.channel.queue_delete(queue=queue_name)
    
    # Publishing
    def publish_message(self, queue_name: str, message: dict, priority: int = 0):
        """Publish a message to a queue.
        
        Args:
            queue_name: Target queue
            message: Message data (will be JSON serialized)
            priority: Message priority (0-9, higher = more important)
        """
        self.create_queue(queue_name)
        
        body = json.dumps({
            'data': message,
            'timestamp': datetime.now().isoformat(),
            'priority': priority
        })
        
        self.channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=body,
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make message persistent
                priority=priority
            )
        )
    
    def publish_task(self, task_type: str, task_data: dict, agent: str = None):
        """Publish a task to the task queue.
        
        Args:
            task_type: Type of task (research, write, review, etc.)
            task_data: Task parameters
            agent: Target agent (optional, for directed tasks)
        """
        queue_name = f"tasks.{agent}" if agent else "tasks.general"
        
        message = {
            'type': task_type,
            'data': task_data,
            'agent': agent,
            'status': 'pending'
        }
        
        self.publish_message(queue_name, message)
    
    # Consuming
    def consume_messages(self, queue_name: str, callback: Callable, auto_ack: bool = False):
        """Consume messages from a queue.
        
        Args:
            queue_name: Queue to consume from
            callback: Function to call for each message
            auto_ack: Automatically acknowledge messages
        """
        self.create_queue(queue_name)
        
        def wrapped_callback(ch, method, properties, body):
            try:
                message = json.loads(body)
                callback(message)
                if not auto_ack:
                    ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                print(f"Error processing message: {e}")
                if not auto_ack:
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=wrapped_callback,
            auto_ack=auto_ack
        )
        
        print(f"Waiting for messages on queue: {queue_name}")
        self.channel.start_consuming()
    
    # Agent-to-Agent messaging
    def send_to_agent(self, from_agent: str, to_agent: str, message_type: str, data: dict):
        """Send a message from one agent to another.
        
        Args:
            from_agent: Sender agent name
            to_agent: Recipient agent name
            message_type: Type of message (handoff, request, response, etc.)
            data: Message data
        """
        queue_name = f"agent.{to_agent}"
        
        message = {
            'from': from_agent,
            'to': to_agent,
            'type': message_type,
            'data': data
        }
        
        self.publish_message(queue_name, message)
    
    def broadcast_to_agents(self, from_agent: str, message_type: str, data: dict):
        """Broadcast a message to all agents.
        
        Args:
            from_agent: Sender agent name
            message_type: Type of message
            data: Message data
        """
        exchange_name = "agent_broadcast"
        
        # Declare fanout exchange
        self.channel.exchange_declare(
            exchange=exchange_name,
            exchange_type='fanout',
            durable=True
        )
        
        message = {
            'from': from_agent,
            'type': message_type,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        
        body = json.dumps(message)
        
        self.channel.basic_publish(
            exchange=exchange_name,
            routing_key='',
            body=body
        )
    
    # Event streaming
    def publish_event(self, event_type: str, event_data: dict):
        """Publish an event to the event stream.
        
        Args:
            event_type: Type of event (task_started, task_completed, etc.)
            event_data: Event data
        """
        exchange_name = "events"
        
        # Declare topic exchange
        self.channel.exchange_declare(
            exchange=exchange_name,
            exchange_type='topic',
            durable=True
        )
        
        message = {
            'type': event_type,
            'data': event_data,
            'timestamp': datetime.now().isoformat()
        }
        
        body = json.dumps(message)
        
        self.channel.basic_publish(
            exchange=exchange_name,
            routing_key=event_type,
            body=body
        )
    
    def subscribe_to_events(self, event_pattern: str, callback: Callable):
        """Subscribe to events matching a pattern.
        
        Args:
            event_pattern: Event pattern (e.g., "task.*", "agent.coordinator.*")
            callback: Function to call for each event
        """
        exchange_name = "events"
        
        # Declare exchange
        self.channel.exchange_declare(
            exchange=exchange_name,
            exchange_type='topic',
            durable=True
        )
        
        # Create exclusive queue
        result = self.channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        
        # Bind queue to exchange with pattern
        self.channel.queue_bind(
            exchange=exchange_name,
            queue=queue_name,
            routing_key=event_pattern
        )
        
        def wrapped_callback(ch, method, properties, body):
            try:
                event = json.loads(body)
                callback(event)
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                print(f"Error processing event: {e}")
        
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=wrapped_callback
        )
        
        print(f"Subscribed to events: {event_pattern}")
        self.channel.start_consuming()
    
    # Dead letter queue
    def setup_dlq(self, queue_name: str):
        """Setup dead letter queue for failed messages.
        
        Args:
            queue_name: Original queue name
        """
        dlq_name = f"{queue_name}.dlq"
        
        # Create DLQ
        self.channel.queue_declare(queue=dlq_name, durable=True)
        
        # Create main queue with DLQ
        self.channel.queue_declare(
            queue=queue_name,
            durable=True,
            arguments={
                'x-dead-letter-exchange': '',
                'x-dead-letter-routing-key': dlq_name
            }
        )


# Singleton instance
_message_broker = None


def get_message_broker() -> MessageBroker:
    """Get MessageBroker instance."""
    global _message_broker
    if _message_broker is None:
        _message_broker = MessageBroker()
    return _message_broker
