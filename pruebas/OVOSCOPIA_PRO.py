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
ESTADO = ""
contflase = 0
contflase2 = 0


def puerto_disponible(puerto_objetivo):
    puertos = [p.device for p in serial.tools.list_ports.comports()]
    return puerto_objetivo in puertos


def recibir_datos(serial_port):
    global PROCESAR
    print("📡 Escuchando datos...")
    ultimo_dato = time.time()
    try:
        while connected.is_set() and not detener_hilo.is_set():
            if serial_port.in_waiting:
                data = serial_port.readline().decode("utf-8", errors="ignore").strip()
                # print("📨 Recibido:", data)
                if data == "CAP":
                    PROCESAR = True
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


def conectar_serial():
    while not detener_hilo.is_set():
        global serial_port
        if puerto_disponible(PUERTO_COM):
            try:
                print(f"🔌 Intentando conectar a {PUERTO_COM}...")
                ser = serial.Serial(PUERTO_COM, BAUDRATE, timeout=1)
                connected.set()
                detener_hilo.clear()
                print(f"✅ Conectado a {PUERTO_COM}")
                serial_port = ser
                hilo_receptor = threading.Thread(target=recibir_datos, args=(ser,))
                hilo_receptor.start()

                while connected.is_set() and not detener_hilo.is_set():
                    time.sleep(1)

                ser.close()

            except serial.SerialException as e:
                print(f"❌ Error al abrir {PUERTO_COM}: {e}")
                connected.clear()
        else:
            print(f"⏳ Esperando que {PUERTO_COM} esté disponible...")

        time.sleep(5)


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


def obtener_valores_hsv():
    h_min = cv2.getTrackbarPos("H Min", "Sliders HSV")
    h_max = cv2.getTrackbarPos("H Max", "Sliders HSV")
    s_min = cv2.getTrackbarPos("S Min", "Sliders HSV")
    s_max = cv2.getTrackbarPos("S Max", "Sliders HSV")
    v_min = cv2.getTrackbarPos("V Min", "Sliders HSV")
    v_max = cv2.getTrackbarPos("V Max", "Sliders HSV")

    h_min2 = cv2.getTrackbarPos("H Min", "Sliders HSV 2")
    h_max2 = cv2.getTrackbarPos("H Max", "Sliders HSV 2")
    s_min2 = cv2.getTrackbarPos("S Min", "Sliders HSV 2")
    s_max2 = cv2.getTrackbarPos("S Max", "Sliders HSV 2")
    v_min2 = cv2.getTrackbarPos("V Min", "Sliders HSV 2")
    v_max2 = cv2.getTrackbarPos("V Max", "Sliders HSV 2")

    return (
        np.array([h_min, s_min, v_min]),
        np.array([h_max, s_max, v_max]),
        np.array([h_min2, s_min2, v_min2]),
        np.array([h_max2, s_max2, v_max2]),
    )


def obtener_valores_hsv2():

    h_min_red = cv2.getTrackbarPos("H Min Red", "Defectos")
    h_max_red = cv2.getTrackbarPos("H Max Red", "Defectos")
    s_min_red = cv2.getTrackbarPos("S Min Red", "Defectos")
    s_max_red = cv2.getTrackbarPos("S Max Red", "Defectos")
    v_min_red = cv2.getTrackbarPos("V Min Red", "Defectos")
    v_max_red = cv2.getTrackbarPos("V Max Red", "Defectos")

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


def procesar_contornos(frame, contornos, tipo):
    global ovo, fecha_actual, vencimiento, ESTADO
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

            text = f"{tipo} {ESTADO}"
            area_text = f"A: {int(area)}px"
            fecha_actual = datetime.now().strftime("%Y-%m-%d")
            vencimiento = (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d")
            full_text = f"{text}\n{area_text}\nF: {fecha_actual}\nV: {vencimiento}"

            full_text_lines = full_text.split("\n")
            rect_x1, rect_y1 = 10, 10
            rect_x2, rect_y2 = 190, rect_y1 + (len(full_text_lines) * 25) + 20

            draw_rounded_rectangle(
                frame, (rect_x1, rect_y1), (rect_x2, rect_y2), (0, 0, 0), -1, 20
            )
            frame[rect_y1 : rect_y2 - 10, rect_x1:165] = (240, 240, 240)

            y0, dy = rect_y1 + 20, 25
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


def iniciar_camara(serial_port):
    # Ruta del archivo de video
    # Ruta del archivo de video
    video_path = "roto.mp4"  # Reemplaza con la ruta correcta de tu video
    global PROCESAR, una, una2, ovo, ESTADO, contflase2, contflase
    # Abre el archivo de video
    # cap = cv2.VideoCapture(video_path)
    colores_hsv = [[30, 7, 255], [13, 255, 154]]
    huevo = False
    ovo = 0
    ESTADO = ""
    TIPO = ""
    area_fisuras_historial = []
    MAX_HISTORIAL = 5

    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

    cv2.namedWindow("Sliders HSV", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Sliders HSV", 640, 300)

    cv2.namedWindow("Sliders HSV 2", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Sliders HSV 2", 640, 300)

    cv2.namedWindow("Defectos", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Defectos", 500, 200)

    def nothing(x):
        pass

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

    while not detener_hilo.is_set():
        # frame_original = cv2.imread("embrion.jpg")
        # print(serial_port)
        ret, frame_original = cap.read()
        if not ret:
            break
        frame_original = cv2.resize(frame_original, (640, 480))
        if PROCESAR:
            # Guarda el tiempo inicial
            if una == False:
                inicio = time.time()  # iniciamos contado
                print("INICIANDO TIMER")
                una = True
            tiempo_transcurrido = time.time() - inicio

            # Imprime el tiempo transcurrido
            print(f"⏳ Tiempo transcurrido: {tiempo_transcurrido:.2f} segundos")

            # Cuando pasen 5 segundos, termina el ciclo
            if (
                tiempo_transcurrido >= 5
            ):  # tiempo para ver estado de ovo con vision artificial
                if una2 == False:
                    print("✅ ¡Tiempo completado!")
                    # Envía la letra 'A'
                    serial_port.write(b"A\n")  # Envía A seguido de un salto de línea
                    print("OVO CLASIFICADO")
                    una2 = True
                    PROCESAR = False
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
                obtener_valores_hsv()
            )

            mask_normal = cv2.inRange(hsv, lower_normal, upper_normal)
            mask_blanco = cv2.inRange(hsv, lower_blanco, upper_blanco)

            contornos_normal, _ = cv2.findContours(
                mask_normal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            contornos_blanco, _ = cv2.findContours(
                mask_blanco, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )

            procesar_contornos(frame_normal, contornos_normal, "NORMAL")
            procesar_contornos(frame_blanco, contornos_blanco, "BLANCO")

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
                TIPO = ""
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
                ESTADO = ""
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
                ESTADO = ""

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
                            ESTADO = "EMBRION"
                            contflase2 = 0
                        else:
                            contflase2 = contflase2 + 1
                            if contflase2 > 10:
                                ESTADO = "CONSUMO"
                    # print("tipo: "+str(TIPO)+", "+ESTADO)

                if ESTADO != "MALO" and TIPO == "BLANCO" and huevo:
                    # Convertimos a escala de grises
                    # DETECTAR ROJO

                    frame_rojo = result.copy()
                    blur = cv2.GaussianBlur(result, (9, 9), 0)
                    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

                    lower_red, upper_red = obtener_valores_hsv2()
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
                            ESTADO = "EMBRION"
                            contflase = 0
                        else:
                            contflase = contflase + 1
                            if contflase > 10:
                                ESTADO = "CONSUMO"

                    # cv2.imshow("Máscara Roja", mask_rojo)
                    # cv2.imshow("Contornos Rojos", frame_rojo)
                    # print("tipo: "+str(TIPO)+", "+ESTADO)

            except:
                pass
        else:
            frame_final = frame_original

        # cv2.imshow("Resultado Final", result)
        cv2.imshow("Detección Final", frame_final)
        # cv2.imshow("Máscara Detectada", mascara_final)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            print("🛑 Cerrando cámara por orden del usuario...")
            detener_hilo.set()
            break

    cap.release()
    cv2.destroyAllWindows()


# === MAIN ===
if __name__ == "__main__":
    hilo_serial = threading.Thread(target=conectar_serial)
    hilo_serial.start()
    # ⏳ Esperamos a que serial_port esté listo
    while serial_port is None:
        print("⌛ Esperando conexión serial...")
        time.sleep(0.5)

    iniciar_camara(serial_port)  # Se bloquea aquí hasta que se cierre la cámara
    print("✅ Programa finalizado correctamente")
