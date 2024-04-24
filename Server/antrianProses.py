#import library yang dibutuhkan
import pika

class RegistrationClient:
    def __init__(self):
        #Inisialisasi Koneksi RabbitMQ menggunakan koneksi blocking dari library Pika
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))

        #Pembuatan Channel yang nantinya digunakan untuk melakukan operasi seperti mendeklarasikan antrian dan mengirim pesan
        self.channel = self.connection.channel()

        #Mendeklarasikan Antrian
        result = self.channel.queue_declare('', exclusive=True)

        #Menyimpan nama antrian yang telah dibuat ke dalam variabel self.callback_queue
        self.callback_queue = result.method.queue

        #Mengatur Konsumsi Pesan dari Antrian 
        self.channel.basic_consume(queue=self.callback_queue, on_message_callback=self.on_response, auto_ack=True)