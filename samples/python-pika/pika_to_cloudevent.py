# -*- coding: utf-8 -*-
# pylint: disable=C0111,C0103,R0205

import json
import logging
import pika

print('pika version: %s' % pika.__version__)

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host='localhost',
        credentials=pika.PlainCredentials('guest', 'guest')
    )
)

main_channel = connection.channel()
main_channel.exchange_declare(exchange='com.example.events', exchange_type='direct')
queue = main_channel.queue_declare('', exclusive=True).method.queue
main_channel.queue_bind(exchange='com.example.events', queue=queue, routing_key='cloudevent.event.type')

def callback(_ch, _method, properties, body):
    print(json.loads(body))
    print(properties)

main_channel.basic_consume(queue, callback, auto_ack=True)

try:
    main_channel.start_consuming()
finally:
    connection.close()
