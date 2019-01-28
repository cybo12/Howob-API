import pika
import logging

logging.basicConfig(level=logging.INFO)


class MessageQueue():

    rbmq_ip = "XX"
    rbmq_port = 5672
    rbmq_pwd = "PWD"
    rbmq_user = "user"
    rbmq_queue = "discord"

    def __init__(self):
        credentials = pika.PlainCredentials(self.rbmq_user, self.rbmq_pwd)
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.rbmq_ip,
                                      port=self.rbmq_port,
                                      virtual_host='/',
                                      credentials=credentials,
                                      heartbeat=0))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.rbmq_queue, durable=True)

    def publish(self, body, rbmq_queue=rbmq_queue):
        self.channel.basic_publish(exchange='',
                                   routing_key=rbmq_queue,
                                   body=body)

    def close(self):
        self.connection.close()

    def get_channel(self):
        return self.channel


mq = MessageQueue()
