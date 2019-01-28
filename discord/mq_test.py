import pika

rbmq_ip = "XX"
rbmq_port = 5672
rbmq_pwd = "PWD"
rbmq_user = "user"
rbmq_queue = "rts"

credentials = pika.PlainCredentials(rbmq_user, rbmq_pwd)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=rbmq_ip,
                              port=rbmq_port,
                              virtual_host='/',
                              credentials=credentials))
channel = connection.channel()

channel.queue_declare(queue=rbmq_queue, durable=True)


def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)


channel.basic_consume(callback,
                      queue=rbmq_queue,
                      no_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
