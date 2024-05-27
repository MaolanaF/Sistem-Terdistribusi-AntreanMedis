#import library yang dibutuhkan
import pika
import json

#Membuat koneksi antara  Python Anda dengan server RabbitMQ. 
connection = pika.BlockingConnection(pika.ConnectionParameters('sister.southeastasia.cloudapp.azure.com'))

# Fungsi callback yang akan dipanggil setiap kali data pendaftaran diterima dari client
def callback(ch, method, properties, body):
    # Memuat data pendaftaran pasien menggunakan JSON
    patient_data = json.loads(body)
    # Mendapatkan nama klinik dari data pendaftaran pasien
    clinic = patient_data["clinic"]
    # Memeriksa apakah sudah ada antrian di dalam klinik
    if clinic not in clinics:
        # Jika belum, klinik ditambahkan ke variabel clinics dengan daftar pasien kosong dan antrean kosong
        clinics[clinic] = {"patients": [], "queue": []}
    
    # Menghitung nomor antrian berdasarkan jumlah pasien yang sudah ada
    queue_number = len(clinics[clinic]["patients"])
    # Menghitung perkiraan waktu tunggu menggunakan fungsi calculate_estimated_time
    estimated_time = calculate_estimated_time(queue_number)
    # Menambahkan data pasien ke dalam daftar pasien klinik dan detail antrian pasien ke dalam antrean klinik
    clinics[clinic]["patients"].append(patient_data)
    # Menambahkan data detail antrian pasien ke dalam antrean klinik
    clinics[clinic]["queue"].append({"queue_number": queue_number, "estimated_time": estimated_time})
    # Membuat data respons berisi nomor antrian dan perkiraan waktu
    response_data = {"queue_number": queue_number, "estimated_time": estimated_time}
    response_message = json.dumps(response_data)
    # Mengirimkan respons ke client
    ch.basic_publish(exchange='', routing_key=properties.reply_to, properties=pika.BasicProperties(correlation_id=properties.correlation_id), body=response_message)
    # Menandai pesan yang telah diproses
    ch.basic_ack(delivery_tag=method.delivery_tag)

# Fungsi untuk menghitung perkiraan waktu tunggu berdasarkan nomor antrian
def calculate_estimated_time(queue_number):
    # Hitung perkiraan waktu berdasarkan jumlah pasien sebelumnya
    # Di sini, kita asumsikan waktu tunggu rata-rata untuk setiap pasien adalah 5 menit
    return queue_number * 5  # misalnya, 5 menit per pasien

# Inisialisasi channel RabbitMQ
channel = connection.channel()

# Deklarasi antrean pendaftaran
channel.queue_declare(queue='registration_queue')
# Mengatur jumlah pesan yang dapat dikonsumsi pada satu waktu
channel.basic_qos(prefetch_count=1)
# Memastikan bahwa setiap data registrasi yang masuk akan ditangani oleh fungsi callback.
channel.basic_consume(queue='registration_queue', on_message_callback=callback)

print('Menunggu permintaan registrasi...')
# Variabel untuk menyimpan informasi klinik dan antrean pasien
clinics = {}
# Memulai mengonsumsi pesan dari antrean pendaftaran
channel.start_consuming()
