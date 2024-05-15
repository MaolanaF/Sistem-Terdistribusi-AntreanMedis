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
        self.available_clinics = ["Klinik A", "Klinik B", "Klinik C"]  # Daftar klinik yang tersedia

    def on_response(self, ch, method, properties, body):
        if self.correlation_id == properties.correlation_id:
            response = json.loads(body)
            print("Nomor Antrean:", response['queue_number'])
            print("Perkiraan Waktu:", response['estimated_time'])

    def select_clinic(self):
        print("Pilih klinik yang tersedia:")
        for index, clinic in enumerate(self.available_clinics, start=1):
            print(f"{index}. {clinic}")
        choice = int(input("Masukkan nomor klinik: "))
        if choice < 1 or choice > len(self.available_clinics):
            print("Pilihan tidak valid.")
            return None
        return self.available_clinics[choice - 1]

    def register_patient(self):
        clinic = self.select_clinic()
        if clinic:
            patient_data = {
                "nomor_rekam_medis": input("Masukkan Nomor Rekam Medis: "),
                "nama": input("Masukkan Nama Pasien: "),
                "tanggal_lahir": input("Masukkan Tanggal Lahir (YYYY-MM-DD): ")
            }
            self.correlation_id = str(uuid.uuid4())
            self.channel.basic_publish(
                exchange='',
                routing_key='registration_queue',
                properties=pika.BasicProperties(
                    reply_to=self.callback_queue,
                    correlation_id=self.correlation_id,
                ),
                body=json.dumps({"clinic": clinic, "patient_data": patient_data}))
            print("Mendaftar ke klinik", clinic)
            print("Menunggu nomor antrean...")

            while getattr(self, 'response', None) is None:
                self.connection.process_data_events()

            return self.response

# Contoh penggunaan
client = RegistrationClient()
response = client.register_patient()