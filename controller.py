import serial
import threading
import time


class Microcontroller:
    TIEMPO_ESPERA_DATOS = 3  # segundos

    def __init__(self, port="COM4", baudrate=9600, timeout=0.01):
        self.port_name = port
        self.baudrate = baudrate
        self.timeout = timeout  # tiempo de espera en lectura serial
        self.ser = None
        self.running = False
        self.read_thread = None
        self.last_data_time = None
        self.PROCESAR = False
        self.smsController = None

    def setProcesar(self, estado):
        self.PROCESAR = estado

    def getProcesar(self):
        return self.PROCESAR

    def getInformacion(self):
        return self.smsController

    def start(self):
        try:
            self.ser = serial.Serial(
                self.port_name, self.baudrate, timeout=self.timeout
            )
            self.running = True
            self.last_data_time = time.time()
            print(f"Puerto {self.port_name} abierto exitosamente.")
            self.read_thread = threading.Thread(target=self.recibir_datos)
            self.read_thread.daemon = True  # se cerrará con el programa
            self.read_thread.start()
        except serial.SerialException as e:
            print(f"Error al abrir el puerto serial: {e}")

    def stop(self):
        self.running = False
        if self.ser and self.ser.is_open:
            try:
                self.ser.close()
                print(f"Puerto {self.port_name} cerrado.")
            except Exception as e:
                print(f"Error al cerrar el puerto: {e}")
        self.ser = None
        self.read_thread = None
        self.last_data_time = None

    def recibir_datos(self):
        while self.running:
            try:
                if self.ser and self.ser.in_waiting > 0:
                    data = self.ser.readline().decode("utf-8", errors="ignore").strip()
                    if data:
                        self.last_data_time = time.time()
                        print(f"Datos recibidos: {data}")

                        self.smsController = data

                        if data == "CAP":
                            print(f"Datos recibidos: {data}")
                            self.PROCESAR = True
                            self.setProcesar(True)

                            print("COMENSAR PROCESO DE DETECCIÓN")

                else:
                    # verificar si ha pasado el tiempo de espera sin recibir datos
                    if time.time() - self.last_data_time >= self.TIEMPO_ESPERA_DATOS:
                        print(
                            "No se han recibido datos en 3 segundos. Cerrando puerto."
                        )
                        self.stop()
                        break
                time.sleep(0.01)
            except Exception as e:
                print(f"Error en recepción: {e}")
                self.stop()
                break

    def envio_dato(self, mensaje):
        if self.ser and self.ser.is_open:
            try:
                self.ser.write(b"A\n")
                print(f"Mensaje enviado: {mensaje}")
            except Exception as e:
                print(f"Error al enviar datos: {e}")
        else:
            print("Puerto serial no está abierto.")
