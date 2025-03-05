import os
import pandas as pd
import json
from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
from loguru import logger
from groq import Groq
from dotenv import load_dotenv

# 🔹 Cargar variables de entorno
load_dotenv()

GROQ_API_KEY = os.getenv('GROQ_API_KEY')

if not GROQ_API_KEY:
    raise ValueError("⚠️ GROQ_API_KEY no está configurado en las variables de entorno.")

logger.info("Clave API de Groq cargada correctamente.")

qclient = Groq(api_key=GROQ_API_KEY)

# 🔹 Inicializar Flask con configuración para servir frontend
app = Flask(__name__, static_folder="frontend", template_folder="frontend")
CORS(app)  # Permitir acceso desde el frontend

# 🔹 Asegurar que Flask siempre acceda a la ruta absoluta de los datos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Ruta base del proyecto
DATA_FOLDER = os.path.join(BASE_DIR, "data")  # Ruta absoluta de la carpeta data

# 🔹 Servir la página principal (index.html)
@app.route("/")
def home():
    return render_template("index.html")

# 🔹 Servir archivos estáticos (CSS, JS, imágenes)
@app.route("/<path:filename>")
def serve_static(filename):
    return send_from_directory("frontend", filename)

# 🔹 Obtener la lista de archivos disponibles
def obtener_lista_excels():
    try:
        archivos = [f for f in os.listdir(DATA_FOLDER) if f.endswith(".xlsx") or f.endswith(".csv")]
        return archivos
    except Exception as e:
        return []

# 🔹 Cargar datos de un archivo Excel o CSV
def cargar_datos_excel(nombre_archivo):
    try:
        ruta = os.path.join(DATA_FOLDER, nombre_archivo)
        if not os.path.exists(ruta):
            return {"error": f"Archivo {nombre_archivo} no encontrado en {DATA_FOLDER}"}, 404

        if nombre_archivo.endswith(".csv"):
            df = pd.read_csv(ruta, encoding="utf-8", engine="python", on_bad_lines="skip")
        else:
            df = pd.read_excel(ruta, engine="openpyxl")

        return df.to_dict(orient="records")
    except Exception as e:
        return {"error": f"Error al leer {nombre_archivo}: {str(e)}"}

# 🔹 Endpoint para obtener la lista de archivos disponibles
@app.route("/api/lista_excels", methods=["GET"])
def listar_archivos():
    archivos = obtener_lista_excels()
    return jsonify({"archivos": archivos})

# 🔹 Endpoint para procesar datos de un archivo Excel
@app.route("/api/procesar_excel", methods=["POST"])
def procesar_excel():
    data = request.json
    nombre_archivo = data.get("archivo")

    if not nombre_archivo:
        return jsonify({"error": "No se ha proporcionado un archivo"}), 400

    datos = cargar_datos_excel(nombre_archivo)
    if isinstance(datos, dict) and "error" in datos:
        return jsonify(datos), 500

    return jsonify({"datos": datos})

# 🔹 Endpoint del chatbot
@app.route("/api/chat", methods=["POST"])
def chatbot():
    data = request.json
    pregunta = data.get("pregunta")
    datos_json = data.get("datos")

    if not pregunta:
        return jsonify({"error": "No se ha proporcionado una pregunta"}), 400

    if not datos_json:
        return jsonify({"error": "No hay datos procesados"}), 400

    # Convertir datos a texto para la API de Groq (limitado a 5 registros para optimizar)
    datos_texto = json.dumps(datos_json[:5], indent=2)

    # 🔹 Enviar la pregunta a Groq con los datos del archivo
    response = qclient.chat.completions.create(
        messages=[
            {"role": "system", "content": "Eres un analista de datos experto en minería de datos."},
            {"role": "user", "content": f"Usando los siguientes datos, responde la pregunta de forma precisa:\n{datos_texto}\n\nPregunta: {pregunta}"},
        ],
        model="llama3-8B-8192",
        stream=False
    )

    respuesta_groq = response.choices[0].message.content if response.choices else "No tengo información suficiente para responder."
    return jsonify({"respuesta": respuesta_groq})

# 🔹 Ejecutar la aplicación
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
