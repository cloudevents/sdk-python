# -*- coding: utf-8 -*-
# pylint: disable=C0111,C0103,R0205

import logging
import pika
import json

from cloudevents.sdk.event import v02

print('pika version: %s' % pika.__version__)

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host='localhost',
        credentials=pika.PlainCredentials('guest', 'guest')
    )
)

main_channel = connection.channel()
main_channel.exchange_declare(exchange='com.example.events', exchange_type='direct')

event = (
    v02.Event().
    SetContentType("application/json").
    SetData({"name": "denis"}).
    SetEventID("my-id").
    SetSource("<event-source").
    SetEventType("cloudevent.event.type")
)

main_channel.basic_publish(
    exchange='com.example.events',
    routing_key=event.EventType(),
    body=json.dumps(event.Data()),
    properties=pika.BasicProperties(
        content_type='application/json',
        headers={
            'cloudEvents:specversion': event.CloudEventVersion(),
            'cloudEvents:type': event.EventType(),
            'cloudEvents:id': event.EventID(),
            'cloudEvents:source': event.Source()
        }
    )
)
connection.close()
