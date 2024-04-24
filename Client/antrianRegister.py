import pika

#Membuat koneksi antara  Python Anda dengan server RabbitMQ. 
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
