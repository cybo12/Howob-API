import pika
import logging
import sys

if sys.argv[1] == "prod":
    HOST = "rabbitmq_stats_1"
    logging.basicConfig(level=logging.ERROR)
    MQ = "howob"

else:
    HOST = 'XX'
    logging.basicConfig(level=logging.INFO)
    MQ = "dev_howob"


class MessageQueue():

    rbmq_ip = HOST
    rbmq_port = 5672
    rbmq_pwd = "PWD"
    rbmq_user = "user"
    rbmq_queue = MQ

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
        logging.info(f"publish on mq {rbmq_queue} : lenght {len(body)}")
        self.channel.basic_publish(exchange='',
                                   routing_key=rbmq_queue,
                                   body=body)

    def close(self):
        self.connection.close()

    def get_channel(self, rbmq_queue=rbmq_queue):
        return self.channel.queue_declare(queue=rbmq_queue, durable=True)


mq = MessageQueue()
