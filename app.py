# -*- coding: utf-8 -*-
"""
Created on Mon July 1 15:34:08 2024
@author: sebas
"""
# LIBRERIAS GENERALES *****************************************
import os
from flask import Flask, render_template, Response, request, redirect, jsonify, url_for
from flask_socketio import SocketIO, emit, disconnect
from werkzeug.utils import secure_filename
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, Image

# CLASES CREADAS PROPIAS **************************************
from camera import VideoCamera

import eventlet
import pandas as pd

# Necesario para que eventlet funcione correctamente con WebSockets
eventlet.monkey_patch()

app = Flask(
    __name__,
    static_url_path="",
    static_folder="static",
    template_folder="templates",
)

app.config["SECRET_KEY"] = "secret_key_12345"
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

video = VideoCamera()
# video.set_mode("procesada")

connected = False
EXCEL_FILE = "registros_ovoscopia.xlsx"


@app.route("/eliminar_registro", methods=["POST"])
def eliminar_registro():

    verificar_excel()  # Asegurar que el archivo Excel existe

    try:

        datos = request.get_json()
        idpalabra = datos.get("id")

        # Leer todas las hojas del archivo
        excel_data = pd.read_excel(EXCEL_FILE, sheet_name=None)

        # Verificar que la hoja "Categorias" exista
        if "Ovoscopia" not in excel_data:
            return (
                jsonify({"status": False, "message": "Hoja 'Ovoscopia' no encontrada"}),
                404,
            )

        df_palabras = excel_data["Ovoscopia"]

        # Buscar la fila con la categoría y palabra
        fila = df_palabras[(df_palabras["ID"] == int(idpalabra))]

        if fila.empty:
            return jsonify({"error": "Palabra no encontrada"}), 404

        # Filtrar y eliminar la palabra
        nueva_df = df_palabras[(df_palabras["ID"] != int(idpalabra))]

        # Guardar TODAS las hojas en el mismo archivo
        excel_data["Ovoscopia"] = nueva_df
        with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl") as writer:
            for sheet_name, df in excel_data.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)

        return jsonify({"status": True, "message": "Palabra borrada correctamente"})

    except Exception as e:
        return (
            jsonify({"status": False, "message": f"Error al borrar: {str(e)}"}),
            500,
        )


def obtener_todo():
    """Obtiene todas las palabras y categorías desde el archivo Excel."""
    try:
        df_ovoscopia = pd.read_excel(EXCEL_FILE, sheet_name="Ovoscopia")

        # Convertir a listas de diccionarios
        info = df_ovoscopia.to_dict(orient="records")

        return info

    except Exception as e:
        print(f"Error al obtener datos: {str(e)}")
        return [], []


# Función para asegurar que el archivo y las hojas existen
def verificar_excel():
    if not os.path.exists(EXCEL_FILE):
        # Crear un archivo Excel vacío con las hojas "Categorias" y "Palabras"
        with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl") as writer:
            df_categorias = pd.DataFrame(
                columns=[
                    "ID",
                    "Tipo Huevo",
                    "Estado",
                    "Fecha Clasificacion",
                    "Fecha Vencimiento",
                ]
            )
            df_categorias.to_excel(writer, sheet_name="Ovoscopia", index=False)
            return True

    return False


@app.route("/registrar_ovoscopia", methods=["POST"])
def registrar_ovoscopia():
    verificar_excel()  # Asegurar que el archivo existe antes de leerlo

    data = request.get_json()
    tipo = data.get("tipo")
    estado = data.get("estado")
    vencimiento = data.get("vencimiento")

    try:
        df_categoria = pd.read_excel(EXCEL_FILE, sheet_name="Ovoscopia")
    except ValueError:
        df_categoria = pd.DataFrame(
            columns=[
                "ID",
                "Tipo Huevo",
                "Estado",
                "Fecha Clasificacion",
                "Fecha Vencimiento",
            ]
        )

    next_id = df_categoria["ID"].max() + 1 if not df_categoria.empty else 1

    nueva_fila = {
        "ID": next_id,
        "Tipo Huevo": tipo,
        "Estado": estado,
        "Fecha Clasificacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Fecha Vencimiento": vencimiento,
    }

    df_categoria = pd.concat(
        [df_categoria, pd.DataFrame([nueva_fila])], ignore_index=True
    )

    with pd.ExcelWriter(
        EXCEL_FILE, engine="openpyxl", mode="a", if_sheet_exists="replace"
    ) as writer:
        df_categoria.to_excel(writer, sheet_name="Ovoscopia", index=False)

    return jsonify({"success": True, "message": "Nuevo registro agregado exitosamente"})


@app.route("/")
def index():
    if video.state():
        video.stop()

    return render_template("main.html")


# FUNCION PAGINA PRINCIPAL
@app.route("/")
def portada():
    if video.state():
        video.set_mode("procesada")
        video.stop()

    return render_template("main.html")


@app.route("/dashboard")
def dashboard():

    print("mostrar dashboard")

    if video.state():
        print("El estado es: ", video.state())
        video.stop()

    return render_template("dashboard.html")


@app.route("/registros")
def registros():

    if video.state():
        video.set_mode("registros")
        video.stop()

    datosTotal = obtener_todo()

    return render_template("registros.html", datos=datosTotal)


@app.route("/calibracion")
def calibracion():
    variables = 0

    return render_template("calibracion.html", variables=variables)


@app.route("/analyzer", methods=["GET"])
def analyzer():

    if video.state():
        video.set_mode("procesada")
        video.stop()

    return render_template("analizer.html", usuario=0, variables=0)


def video_stream(camera):

    global connected

    try:

        print("mostrar videostream")

        if video.state() == False:
            video.start()

            # time.sleep(0.1)

        last_info = None

        while video.state():
            #  print("obteniendo video")
            frame, info, TIPO, ESTADO, VENCIMIENTO = camera.get_frame()

            # if info != last_info:  # Solo envía si hay cambios
            socketio.emit(
                "update",
                {
                    "sms": info,
                    "TIPO": TIPO,
                    "ESTADO": ESTADO,
                    "VENCIMIENTO": VENCIMIENTO,
                },
            )
            #    last_info = info

            # socketio.sleep(0.1)

            if frame is None:
                break

            socketio.sleep(0.01)

            yield (
                b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n\r\n"
            )

            # yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n\r\n")

    except:

        print("Algo salio mal")


@app.route("/video_feed")
def video_feed():

    print("enviando videooo")
    return Response(
        video_stream(video), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


if __name__ == "__main__":

    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
