import cv2
import numpy as np
from datetime import datetime, timedelta
import serial
import threading
import time
import serial.tools.list_ports


# === CONFIGURACIÓN SERIAL ===
PUERTO_COM = "COM4"
BAUDRATE = 9600
TIEMPO_ESPERA_DATOS = 3

connected = threading.Event()
detener_hilo = threading.Event()
PROCESAR = False
una = False
una2 = False
serial_port = None
fecha_actual = None
vencimiento = None
ovo = 0

contflase = 0
contflase2 = 0
# Crear un hilo para la reproducción de audio
# audio_thread = threading.Thread(target=play_audio1)
# audio_thread.start()
capturar = False
reproducir = True
guardar = False
check = False

imagen_normal = None
imagen_mask = None
imagen_pseudo = None
imagen_procesada = None


class Controller(object):
    def __init__(self):
        self.stateController = False
        self.PROCESAR = False

    def start(self):

        if self.stateController == False:
            self.stateController = True

            hilo_serial = threading.Thread(target=self.conectar_serial)
            hilo_serial.start()
            # ⏳ Esperamos a que serial_port esté listo
            while serial_port is None:
                print("⌛ Esperando conexión serial...")
                time.sleep(0.5)

    def stop(self):
        global connected, detener_hilo
        connected.clear()
        detener_hilo.set()
        self.stateController = False
        print("🔌 Desconectado del puerto")

    def state(self):
        return self.stateCam

    def set_mode(self, dato):
        self.camera_mode = dato

    def set_Capturar(self):
        global capturar, reproducir
        capturar = True
        reproducir = False

    def set_reproducir(self):
        global capturar, reproducir
        reproducir = True
        capturar = False

    def set_check(self, estado):
        global check
        if estado == "True":
            check = True
        elif estado == "False":
            check = False

    def get_check(self):
        global check
        return check

    def puerto_disponible(self, puerto_objetivo):
        puertos = [p.device for p in serial.tools.list_ports.comports()]
        return puerto_objetivo in puertos

    def getProcesar(self):
        return self.PROCESAR

    def setProcesar(self, estado):
        self.PROCESAR = estado

    def envioDato(self):
        global serial_port
        serial_port.write(b"A\n")

    def recibir_datos(self, serial_port):
        global PROCESAR, detener_hilo
        print("📡 Escuchando datos...")
        ultimo_dato = time.time()
        try:
            while connected.is_set() and not detener_hilo.is_set():
                if serial_port.in_waiting:
                    data = (
                        serial_port.readline().decode("utf-8", errors="ignore").strip()
                    )
                    print("📨 Recibido:", data)
                    if data == "CAP":
                        self.PROCESAR = True
                        print("COMENSAR PROCESO DE DETECCIÓN")

                    ultimo_dato = time.time()
                else:
                    if time.time() - ultimo_dato > TIEMPO_ESPERA_DATOS:
                        print("⚠️ Sin datos por más de 5s, posible desconexión")
                        break
                time.sleep(0.01)
        except serial.SerialException as e:
            print(f"⚠️ Error de puerto: {e}")
        finally:
            connected.clear()
            detener_hilo.set()
            print("🔌 Desconectado del puerto")

    def conectar_serial(self):
        while not detener_hilo.is_set():
            global serial_port
            if self.puerto_disponible(PUERTO_COM):

                print(f"🔌 Intentando conectar a {PUERTO_COM}...")
                ser = serial.Serial(PUERTO_COM, BAUDRATE, timeout=1)
                connected.set()
                detener_hilo.clear()
                print(f"✅ Conectado a {PUERTO_COM}")
                serial_port = ser
                hilo_receptor = threading.Thread(target=self.recibir_datos, args=(ser,))
                hilo_receptor.start()

                while connected.is_set() and not detener_hilo.is_set():
                    time.sleep(1)

                ser.close()

            else:
                print(f"⏳ Esperando que {PUERTO_COM} esté disponible...")

            time.sleep(5)
