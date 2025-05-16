import cv2
import numpy as np
from datetime import datetime, timedelta
import serial
import threading
import time
import serial.tools.list_ports

from controller import Microcontroller

# from microcontroller import Controller

from werkzeug.serving import run_simple
import os


# Registrar la función que se ejecutará al cerrar

# === CONFIGURACIÓN SERIAL ===
PUERTO_COM = "COM4"
BAUDRATE = 9600
TIEMPO_ESPERA_DATOS = 3

esp32 = Microcontroller(port=PUERTO_COM, baudrate=BAUDRATE)
# esp32 = Controller()
# esp32.start()

PROCESAR = False
una = False
una2 = False
serial_port = None
fecha_actual = None
vencimiento = None
ovo = 0
ESTADO = ""
contflase = 0
contflase2 = 0
# Crear un hilo para la reproducción de audio
# audio_thread = threading.Thread(target=play_audio1)
# audio_thread.start()

PORC1 = "---"
PORC2 = "---"
TIPO1 = ""
TIPO2 = ""

xLeft = "0"
yLeft = "0"
xRight = "0"
yRight = "0"


pseudo_color = None
colocarBien = ""

capturar = False
reproducir = True
guardar = False
check = False

imagen_normal = None
imagen_mask = None
imagen_pseudo = None
imagen_procesada = None

inicio = 0


# Función para mostrar el mensaje de "Sin cámara"
def mostrar_mensaje_sin_camara():
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.putText(
        frame,
        "Sin camara",
        (200, 240),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )
    return frame


# === DETECCIÓN CON CÁMARA ===


def draw_rounded_rectangle(img, top_left, bottom_right, color, thickness, radius):
    cv2.rectangle(
        img,
        (top_left[0] + radius, top_left[1]),
        (bottom_right[0] - radius, bottom_right[1]),
        color,
        thickness,
    )
    cv2.rectangle(
        img,
        (top_left[0], top_left[1] + radius),
        (bottom_right[0], bottom_right[1] - radius),
        color,
        thickness,
    )
    cv2.circle(
        img, (top_left[0] + radius, top_left[1] + radius), radius, color, thickness
    )
    cv2.circle(
        img, (bottom_right[0] - radius, top_left[1] + radius), radius, color, thickness
    )
    cv2.circle(
        img, (top_left[0] + radius, bottom_right[1] - radius), radius, color, thickness
    )
    cv2.circle(
        img,
        (bottom_right[0] - radius, bottom_right[1] - radius),
        radius,
        color,
        thickness,
    )


def obtener_valores_hsv(
    lower_h,
    lower_s,
    lower_v,
    upper_h,
    upper_s,
    upper_v,
    lower_h2,
    lower_s2,
    lower_v2,
    upper_h2,
    upper_s2,
    upper_v2,
):
    h_min = lower_h
    h_max = upper_h
    s_min = lower_s
    s_max = upper_s
    v_min = lower_v
    v_max = upper_v
    h_min2 = lower_h2
    h_max2 = upper_h2
    s_min2 = lower_s2
    s_max2 = upper_s2
    v_min2 = lower_v2
    v_max2 = upper_v2

    return (
        np.array([h_min, s_min, v_min]),
        np.array([h_max, s_max, v_max]),
        np.array([h_min2, s_min2, v_min2]),
        np.array([h_max2, s_max2, v_max2]),
    )


def obtener_valores_hsv2(lower_h, lower_s, lower_v, upper_h, upper_s, upper_v):

    h_min_red = lower_h
    h_max_red = upper_h
    s_min_red = lower_s
    s_max_red = upper_s
    v_min_red = lower_v
    v_max_red = upper_v

    return (
        np.array([h_min_red, s_min_red, v_min_red]),
        np.array([h_max_red, s_max_red, v_max_red]),
    )


def es_forma_de_huevo(contorno):
    # Aproximar el contorno a una elipse
    if len(contorno) >= 5:
        ellipse = cv2.fitEllipse(contorno)
        (center, axes, angle) = ellipse

        # Verificar la relación de los ejes mayor y menor para determinar si tiene forma de huevo
        ratio = max(axes) / min(axes)  # Relación entre los ejes mayor y menor
        if (
            1 < ratio < 2
        ):  # Ajusta el rango de esta relación según lo que consideres forma de huevo
            return True
    return False


def procesar_contornos(frame, contornos, tipo, estado):
    global ovo, fecha_actual, vencimiento
    for contorno in contornos:
        area = cv2.contourArea(contorno)
        if area < 30000:
            continue

        # Verificar si tiene forma de huevo
        if es_forma_de_huevo(contorno):
            cv2.drawContours(
                frame, [contorno], -1, (225, 20, 55), 3
            )  # Dibuja solo contornos válidos
            ovo = contorno
            M = cv2.moments(contorno)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
            else:
                cX, cY = 0, 0

            cv2.circle(frame, (cX, cY), 7, (255, 0, 0), -1)

            text = f"{tipo}:{estado}"
            area_text = f"A: {int(area)}px"
            fecha_actual = datetime.now().strftime("%Y-%m-%d")
            # vencimiento = (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d")

            vencimiento = (datetime.now()).strftime("%Y-%m-%d")

            full_text = f"{text}\n{area_text}\nF: {fecha_actual}\nV: {vencimiento}"

            full_text_lines = full_text.split("\n")
            rect_x1, rect_y1 = 10, 10
            rect_x2, rect_y2 = 190, rect_y1 + (len(full_text_lines) * 25) + 20

            # draw_rounded_rectangle(
            #    frame, (rect_x1, rect_y1), (rect_x2, rect_y2), (0, 0, 0), -1, 20
            # )

            # frame[rect_y1 : rect_y2 - 10, rect_x1:165] = (240, 240, 240)

            y0, dy = rect_y1 + 20, 25

            """
            for i, line in enumerate(full_text_lines):
                cv2.putText(
                    frame,
                    line,
                    (rect_x1 + 10, y0 + i * dy),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 0, 0),
                    1,
                    cv2.LINE_AA,
                )
            """


def procesamiento(
    img,
    lower_h,
    lower_s,
    lower_v,
    upper_h,
    upper_s,
    upper_v,
    lower_h2,
    lower_s2,
    lower_v2,
    upper_h2,
    upper_s2,
    upper_v2,
    lower_h3,
    lower_s3,
    lower_v3,
    upper_h3,
    upper_s3,
    upper_v3,
):

    global vencimiento, una, una2, ovo, ESTADO, contflase2, contflase, esp32, inicio, PROCESAR, capturar, reproducir, colocarBien, check, xLeft, yLeft, xRight, yRight, imagen_normal, imagen_mask, imagen_pseudo, imagen_procesada
    # DESCOMENTAR PARA Q FUNCIONE CAMARA

    # DESCOMENTAR PARA Q FUNCIONE IMAGEN
    # frame = frame_original.copy()

    try:

        PROCESAR = esp32.getProcesar()

        # Abre el archivo de video
        # cap = cv2.VideoCapture(video_path)
        colores_hsv = [[30, 7, 255], [13, 255, 154]]
        huevo = False
        ovo = 0
        ESTADO = ""
        TIPO = ""
        area_fisuras_historial = []
        MAX_HISTORIAL = 5

        # cv2.namedWindow("Sliders HSV", cv2.WINDOW_NORMAL)
        # cv2.resizeWindow("Sliders HSV", 640, 300)

        # cv2.namedWindow("Sliders HSV 2", cv2.WINDOW_NORMAL)
        # cv2.resizeWindow("Sliders HSV 2", 640, 300)

        # cv2.namedWindow("Defectos", cv2.WINDOW_NORMAL)
        # cv2.resizeWindow("Defectos", 500, 200)

        def nothing(x):
            pass

        """
        
        # Rango para huevo normal
        cv2.createTrackbar("H Min", "Sliders HSV", 0, 179, nothing)
        cv2.createTrackbar("H Max", "Sliders HSV", 14, 179, nothing)
        cv2.createTrackbar("S Min", "Sliders HSV", 22, 255, nothing)
        cv2.createTrackbar("S Max", "Sliders HSV", 255, 255, nothing)
        cv2.createTrackbar("V Min", "Sliders HSV", 21, 255, nothing)  # 16
        cv2.createTrackbar("V Max", "Sliders HSV", 255, 255, nothing)

        # Rango para huevo blanco
        cv2.createTrackbar("H Min", "Sliders HSV 2", 0, 179, nothing)
        cv2.createTrackbar("H Max", "Sliders HSV 2", 56, 179, nothing)
        cv2.createTrackbar("S Min", "Sliders HSV 2", 0, 255, nothing)
        cv2.createTrackbar("S Max", "Sliders HSV 2", 200, 255, nothing)
        cv2.createTrackbar("V Min", "Sliders HSV 2", 200, 255, nothing)
        cv2.createTrackbar("V Max", "Sliders HSV 2", 255, 255, nothing)

        # Rango para color rojo defectos
        cv2.createTrackbar("H Min Red", "Defectos", 0, 179, nothing)
        cv2.createTrackbar("H Max Red", "Defectos", 37, 255, nothing)
        cv2.createTrackbar("S Min Red", "Defectos", 85, 255, nothing)
        cv2.createTrackbar("S Max Red", "Defectos", 255, 255, nothing)
        cv2.createTrackbar("V Min Red", "Defectos", 146, 255, nothing)
        cv2.createTrackbar("V Max Red", "Defectos", 255, 255, nothing)
        """

        # frame_original = cv2.imread("embrion.jpg")
        # print(serial_port)

        frame_original = cv2.resize(img, (640, 480))
        if PROCESAR:
            # Guarda el tiempo inicial
            if una == False:
                inicio = time.time()  # iniciamos contado
                print("INICIANDO TIMER")
                una = True
            tiempo_transcurrido = time.time() - inicio

            # Imprime el tiempo transcurrido
            # print(f"⏳ Tiempo transcurrido: {tiempo_transcurrido:.2f} segundos")

            # Cuando pasen 5 segundos, termina el ciclo
            if (
                tiempo_transcurrido >= 3
            ):  # tiempo para ver estado de ovo con vision artificial
                if una2 == False:
                    print("✅ ¡Tiempo completado!")
                    # Envía la letra 'A'
                    # serial_port.write(b"A\n")  # Envía A seguido de un salto de línea

                    esp32.envio_dato("A\n")
                    print("OVO CLASIFICADO")
                    una2 = True
                    PROCESAR = False

                    esp32.setProcesar(PROCESAR)

                    una2 = False
                    una = False
                    tiempo_transcurrido = 0
                    contflase = 0
                    contflase2 = 0
                    print(
                        "Huevo clasificado como tipo: "
                        + str(TIPO)
                        + ", estado: "
                        + ESTADO
                    )
                    if ESTADO == "MALO":
                        print("No se puede consumir")
                    else:
                        print(
                            "Fecha actual: "
                            + str(fecha_actual)
                            + ", Fecha vencimiento: "
                            + str(vencimiento)
                        )

            # Redimensiona el frame a 640x480

            frame_normal = frame_original.copy()
            frame_blanco = frame_original.copy()

            blur = cv2.GaussianBlur(frame_original, (9, 9), 0)
            hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

            lower_normal, upper_normal, lower_blanco, upper_blanco = (
                obtener_valores_hsv(
                    lower_h,
                    lower_s,
                    lower_v,
                    upper_h,
                    upper_s,
                    upper_v,
                    lower_h2,
                    lower_s2,
                    lower_v2,
                    upper_h2,
                    upper_s2,
                    upper_v2,
                )
            )

            mask_normal = cv2.inRange(hsv, lower_normal, upper_normal)
            mask_blanco = cv2.inRange(hsv, lower_blanco, upper_blanco)

            contornos_normal, _ = cv2.findContours(
                mask_normal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            contornos_blanco, _ = cv2.findContours(
                mask_blanco, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )

            procesar_contornos(frame_normal, contornos_normal, "NORMAL", ESTADO)
            procesar_contornos(frame_blanco, contornos_blanco, "BLANCO", ESTADO)

            area_normal = sum(
                cv2.contourArea(c)
                for c in contornos_normal
                if cv2.contourArea(c) >= 30000
            )
            area_blanco = sum(
                cv2.contourArea(c)
                for c in contornos_blanco
                if cv2.contourArea(c) >= 30000
            )

            if area_normal > area_blanco and area_normal > 0:
                frame_final = frame_normal
                mascara_final = mask_normal
                TIPO = "NORMAL"
                # print("ovo detectado")
                huevo = True
            elif area_blanco > 0:
                frame_final = frame_blanco
                mascara_final = mask_blanco
                TIPO = "BLANCO"
                # print("ovo detectado")
                huevo = True
            else:
                frame_final = frame_original
                TIPO = "OTRO"
                huevo = False
                mascara_final = np.zeros_like(mask_normal)

            # Encuentra el contorno más grande en la máscara final
            contornos, _ = cv2.findContours(
                mascara_final, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )

            if contornos:
                # Ordena por área y toma el más grande
                contorno_max = max(contornos, key=cv2.contourArea)
                # Crea una nueva máscara completamente rellena del contorno más grande
                mascara_rellena = np.zeros_like(mascara_final)
                cv2.drawContours(
                    mascara_rellena, [contorno_max], -1, 255, thickness=cv2.FILLED
                )
                # Aplica esta nueva máscara rellena al frame original
                result = cv2.bitwise_and(
                    frame_original, frame_original, mask=mascara_rellena
                )

                # Si deseas también recortar al bounding box del contorno:
                # x, y, w, h = cv2.boundingRect(contorno_max)
                # result_cortado = result[y:y+h, x:x+w]
                # Muestra el resultado
                # cv2.imshow("Huevo recortado", result_cortado)

            # comprobar fisuras en el ovo
            try:

                frame_final2 = result.copy()
                frame_final3 = result.copy()
                frame_final4 = result.copy()
                ESTADO = "CONSUMO"
                # Convertimos a escala de grises
                gris = cv2.cvtColor(frame_final2, cv2.COLOR_BGR2GRAY)
                # Threshold adaptativo
                thresh = cv2.adaptiveThreshold(
                    gris,
                    255,
                    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                    cv2.THRESH_BINARY_INV,
                    15,
                    15,
                )
                # Creamos una máscara desde el contorno del huevo (ovo)
                mascara_ovo = np.zeros_like(gris)

                # cv2.imshow("Máscar", thresh)
                cv2.drawContours(mascara_ovo, [ovo], -1, 255, cv2.FILLED)
                # Erosionamos la máscara para reducirla unos cuantos píxeles hacia adentro
                kernel = np.ones((15, 15), np.uint8)
                mascara_ovo_erosionada = cv2.erode(mascara_ovo, kernel, iterations=1)
                # Aplicamos la máscara erosionada al threshold para evitar contorno exterior

                thresh_dentro = cv2.bitwise_and(
                    thresh, thresh, mask=mascara_ovo_erosionada
                )
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 1))

                eroded_img = cv2.erode(thresh_dentro, kernel)
                # Detectamos contornos internos (fisuras) solo dentro del área erosionada y limpia
                contornos, _ = cv2.findContours(
                    eroded_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
                )
                area_total_fisuras = 0

                # cv2.imshow("Máscar", eroded_img)
                for cnt in contornos:
                    area = cv2.contourArea(cnt)
                    if 15 <= area <= 370:
                        cv2.drawContours(frame_final, [cnt], -1, (120, 0, 120), 2)
                        area_total_fisuras += area

                # Actualiza historial de áreas
                area_fisuras_historial.append(area_total_fisuras)
                if len(area_fisuras_historial) > MAX_HISTORIAL:
                    area_fisuras_historial.pop(0)

                # Calcula media del área de fisuras
                media_fisuras = sum(area_fisuras_historial) / len(
                    area_fisuras_historial
                )
                # print(media_fisuras)

                if media_fisuras > 20:
                    # print("ovo roto: "+str(media_fisuras) +" area afectada")
                    ESTADO = "MALO"
                    # print("tipo: "+str(TIPO)+", "+ESTADO)

                # if ESTADO=="MALO":
                #   cv2.imshow("Fisuras internas", eroded_img)
                else:
                    # COMPROBAR MANCHAS Y SUCIEDAD

                    gris4 = cv2.cvtColor(frame_final4, cv2.COLOR_BGR2GRAY)
                    # Aplicamos un suavizado fuerte para eliminar microdetalles de brillo
                    gris4_blur = cv2.GaussianBlur(gris4, (15, 15), 0)
                    # Threshold adaptativo sobre la imagen suavizada
                    thresh4 = cv2.adaptiveThreshold(
                        gris4_blur,
                        255,
                        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                        cv2.THRESH_BINARY_INV,
                        65,
                        9,
                    )
                    # Crear una máscara del contorno 'ovo' (el huevo)
                    mask_ovo = np.zeros_like(thresh4)
                    cv2.drawContours(
                        mask_ovo, [ovo], -1, 255, -1
                    )  # Dibuja y rellena el contorno en blanco
                    # Erosionar la máscara para evitar bordes exteriores
                    kernel = np.ones((5, 5), np.uint8)
                    mascara_ovo_erosionada = cv2.erode(mask_ovo, kernel, iterations=2)
                    # Aplicamos la máscara erosionada al threshold para trabajar SOLO dentro del huevo
                    thresh_dentro4 = cv2.bitwise_and(
                        thresh4, thresh4, mask=mascara_ovo_erosionada
                    )
                    # Detectamos contornos dentro del área válida
                    contornos4, _ = cv2.findContours(
                        thresh_dentro4, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
                    )

                    # Recorrer contornos detectados
                    for cnt4 in contornos4:
                        area4 = cv2.contourArea(cnt4)

                        if 80 <= area4 <= 1770:  # Filtro por área

                            # Creamos una máscara temporal de este contorno
                            mask_temp = np.zeros_like(gris4)
                            cv2.drawContours(mask_temp, [cnt4], -1, 255, -1)

                            # Calculamos la media de los canales B, G, R DENTRO del contorno
                            mean_val_bgr = cv2.mean(
                                frame_final4, mask=mask_temp
                            )  # (B, G, R, _)

                            # Extraemos los valores
                            mean_B = mean_val_bgr[0]
                            mean_G = mean_val_bgr[1]
                            mean_R = mean_val_bgr[2]

                            # Filtro: todas las componentes deben ser bajas (verdaderamente negro)
                            if mean_B < 40 and mean_G < 40 and mean_R < 150:
                                cv2.drawContours(
                                    frame_final, [cnt4], -1, (150, 0, 20), 2
                                )
                                ESTADO = "MALO"
                                # print("tipo: "+str(TIPO)+", "+ESTADO)
                                # print("suciedad")

                    # Mostrar resultados
                    # cv2.imshow("Gris original", gris4)
                    # cv2.imshow("Gris suavizado", gris4_blur)
                    # cv2.imshow("Threshold adaptativo", thresh4)
                    # cv2.imshow("Mascara ovo erosionada", mascara_ovo_erosionada)
                    # cv2.imshow("Threshold dentro del huevo", thresh_dentro4)
                    # cv2.imshow("Manchas oscuras detectadas", frame_final4)

            except:
                pass
                ESTADO = "ERROR"

            # DETECTAR EMBRION

            try:

                if ESTADO != "MALO" and TIPO == "NORMAL" and huevo:
                    # Convertimos a escala de grises
                    gris2 = cv2.cvtColor(frame_final3, cv2.COLOR_BGR2GRAY)
                    # Threshold adaptativo
                    thresh2 = cv2.adaptiveThreshold(
                        gris2,
                        255,
                        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                        cv2.THRESH_BINARY_INV,
                        17,
                        5,
                    )

                    # Creamos una máscara desde el contorno del huevo (ovo)
                    mascara_ovo2 = np.zeros_like(gris2)
                    # cv2.drawContours(mascara_ovo, [ovo], -1, 255, cv2.FILLED)

                    # Erosionamos la máscara para reducirla unos cuantos píxeles hacia adentro
                    kernel2 = np.ones((15, 15), np.uint8)
                    mascara_ovo_erosionada2 = cv2.erode(
                        mascara_ovo2, kernel2, iterations=1
                    )
                    # Aplicamos la máscara erosionada al threshold para evitar contorno exterior
                    thresh_dentro2 = cv2.bitwise_and(
                        thresh2, thresh2, mask=mascara_ovo_erosionada
                    )
                    kernel2 = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
                    eroded_img2 = cv2.erode(thresh_dentro2, kernel2)
                    # Detectamos contornos internos (fisuras) solo dentro del área erosionada y limpia
                    contornos2, _ = cv2.findContours(
                        eroded_img2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
                    )

                    # cv2.imshow("embrion", eroded_img2)
                    # cv2.imshow("Fisuras inter", thresh)

                    for cnt in contornos2:
                        area = cv2.contourArea(cnt)
                        if 15 <= area <= 370:
                            cv2.drawContours(frame_final, [cnt], -1, (120, 0, 120), 1)
                            ESTADO = "EMBRIÓN"
                            contflase2 = 0
                            vencimiento = (datetime.now() + timedelta(days=7)).strftime(
                                "%Y-%m-%d"
                            )

                        else:
                            contflase2 = contflase2 + 1
                            if contflase2 > 10:
                                ESTADO = "CONSUMO"
                                vencimiento = (
                                    datetime.now() + timedelta(days=21)
                                ).strftime("%Y-%m-%d")

                    # print("tipo: "+str(TIPO)+", "+ESTADO)

                if ESTADO != "MALO" and TIPO == "BLANCO" and huevo:
                    # Convertimos a escala de grises
                    # DETECTAR ROJO

                    frame_rojo = result.copy()
                    blur = cv2.GaussianBlur(result, (9, 9), 0)
                    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

                    lower_red, upper_red = obtener_valores_hsv2(
                        lower_h3, lower_s3, lower_v3, upper_h3, upper_s3, upper_v3
                    )
                    mask_rojo = cv2.inRange(hsv, lower_red, upper_red)
                    contornos_rojo, _ = cv2.findContours(
                        mask_rojo, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
                    )

                    # Procesar solo contornos con área mayor a 300
                    for contorno in contornos_rojo:
                        area = cv2.contourArea(contorno)
                        # print(area)
                        if area > 300:
                            cv2.drawContours(
                                frame_final, [contorno], -1, (0, 0, 255), 2
                            )
                            ESTADO = "EMBRIÓN"
                            contflase = 0
                            vencimiento = (datetime.now() + timedelta(days=7)).strftime(
                                "%Y-%m-%d"
                            )
                        else:
                            contflase = contflase + 1
                            if contflase > 10:
                                ESTADO = "CONSUMO"
                                vencimiento = (
                                    datetime.now() + timedelta(days=21)
                                ).strftime("%Y-%m-%d")

                    # cv2.imshow("Máscara Roja", mask_rojo)
                    # cv2.imshow("Contornos Rojos", frame_rojo)
                # print("tipoOOO: " + str(TIPO) + ", " + ESTADO)

            except:
                pass
        else:
            frame_final = frame_original

        # cv2.imshow("Resultado Final", result)
        # cv2.imshow("Detección Final", frame_final)

        return frame_final, TIPO, ESTADO, vencimiento

    # cv2.imshow('Imagen Pseudo Color', pseudo_color)
    except Exception as e:
        print("sin camara:")
        print(e)
        frame = mostrar_mensaje_sin_camara()
        return frame
        # cv2.imshow('Detectar Contornos pies', frame)

        # Salir del bucle si se presiona la tecla 'q'

    # image = frame
    # image = cv2.resize(image, (640, 480))

    # image = cv2.imencode(".jpg", planta)[1].tobytes()


class VideoCamera(object):
    def __init__(self):

        self.camera_mode = ""
        self.stateCam = False

        self.lower_h = 0
        self.lower_s = 22
        self.lower_v = 21
        self.upper_h = 14
        self.upper_s = 255
        self.upper_v = 255

        self.lower_h2 = 0
        self.lower_s2 = 56
        self.lower_v2 = 0
        self.upper_h2 = 200
        self.upper_s2 = 200
        self.upper_v2 = 255

        # PARA DEFECTOS

        self.lower_h3 = 0
        self.lower_s3 = 85
        self.lower_v3 = 146
        self.upper_h3 = 37
        self.upper_s3 = 255
        self.upper_v3 = 255

        # self.cap = None

        # hilo_serial = threading.Thread(target=self.conectar_serial)
        # hilo_serial.start()
        # ⏳ Esperamos a que serial_port esté listo
        # while serial_port is None:
        #    print("⌛ Esperando conexión serial...")
        #    time.sleep(0.5)

    def start(self):

        if self.stateCam == False:
            self.stateCam = True
            # Abrir la camara rapido con CAP_DSHOW
            self.cap = cv2.VideoCapture(1)
            esp32.start()

        # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        # self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        # self.cap.set(10, 150)
        # self.cap.set(28, 0)

    def stop(self):

        if self.stateCam:
            self.stateCam = False
            self.stop_controller()

        self.cap.release()
        print("DETUVE EL VIDEO")

    def state(self):
        return self.stateCam

    def set_mode(self, dato):
        self.camera_mode = dato

    def set_hsv_val(self, tipo, valor):

        valor = int(valor)

        if tipo == "lower-h":
            self.lower_h = valor
        elif tipo == "lower-s":
            self.lower_s = valor
        elif tipo == "lower-v":
            self.lower_v = valor
        elif tipo == "upper-h":
            self.upper_h = valor
        elif tipo == "upper-s":
            self.upper_s = valor
        elif tipo == "upper-v":
            self.upper_v = valor
        elif tipo == "lower-h-dedos":
            self.lower_h2 = valor
        elif tipo == "lower-s-dedos":
            self.lower_s2 = valor
        elif tipo == "lower-v-dedos":
            self.lower_v2 = valor
        elif tipo == "upper-h-dedos":
            self.upper_h2 = valor
        elif tipo == "upper-s-dedos":
            self.upper_s2 = valor
        elif tipo == "upper-v-dedos":
            self.upper_v2 = valor

    def __del__(self):

        if self.cap.isOpened():
            self.cap.release()

    def get_variables(self):
        return (
            self.lower_h,
            self.lower_s,
            self.lower_v,
            self.upper_h,
            self.upper_s,
            self.upper_v,
            self.lower_h2,
            self.lower_s2,
            self.lower_v2,
            self.upper_h2,
            self.upper_s2,
            self.upper_v2,
        )

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

    def get_images(self):
        global imagen_normal, imagen_mask, imagen_pseudo, imagen_procesada
        return imagen_normal, imagen_mask, imagen_pseudo, imagen_procesada

    def stop_controller(self):
        global esp32
        esp32.stop()

    def get_frame(self):

        success, frame = self.cap.read()
        if not success:
            return None
        else:
            frame2, TIPO, ESTADO, VENCIMIENTO = procesamiento(
                frame,
                self.lower_h,
                self.lower_s,
                self.lower_v,
                self.upper_h,
                self.upper_s,
                self.upper_v,
                self.lower_h2,
                self.lower_s2,
                self.lower_v2,
                self.upper_h2,
                self.upper_s2,
                self.upper_v2,
                self.lower_h3,
                self.lower_s3,
                self.lower_v3,
                self.upper_h3,
                self.upper_s3,
                self.upper_v3,
            )

        ret, buffer = cv2.imencode(".jpg", frame2)

        return buffer.tobytes(), esp32.getInformacion(), TIPO, ESTADO, VENCIMIENTO

        # image=cv2.resize(image,(840,640))
        # if success:
        #    image = procesamiento(image)
        # so we must encode it into JPEG in order to correctly display the video stream.

    # ret, jpeg = cv2.imencode(".jpg", image)

    # print("obteniendo video")
    # return jpeg.tobytes()
