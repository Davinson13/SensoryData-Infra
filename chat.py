import os
import pandas as pd
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from loguru import logger
from groq import Groq
from dotenv import load_dotenv

# 🔹 Cargar variables de entorno
load_dotenv()

logger.info(os.getenv('GROQ_API_KEY'))

qclient = Groq()

# 🔹 Inicializar Flask
app = Flask(__name__)
CORS(app)  # Permitir acceso desde el frontend

# 🔹 Ruta de los archivos Excel
DATA_FOLDER = "SensoryData/Data/"

# 🔹 Obtener la lista de archivos disponibles
def obtener_lista_excels():
    try:
        archivos = [f for f in os.listdir(DATA_FOLDER) if f.endswith(".xlsx") or f.endswith(".csv")]
        return archivos
    except Exception as e:
        return []

def cargar_datos_excel(nombre_archivo):
    try:
        ruta = os.path.join(DATA_FOLDER, nombre_archivo)
        if not os.path.exists(ruta):
            return {"error": f"Archivo {nombre_archivo} no encontrado en {DATA_FOLDER}"}, 404

        if nombre_archivo.endswith(".csv"):
            df = pd.read_csv(ruta, encoding="utf-8", engine="python", error_bad_lines=False)
        else:
            df = pd.read_excel(ruta, engine="openpyxl")

        return df.to_dict(orient="records")
    except Exception as e:
        return {"error": f"Error al leer {nombre_archivo}: {str(e)}"}
    
@app.route("/")
def home():
    return "Bienvenido al Chatbot con Datos de Sensores"

# 🔹 Endpoint para obtener la lista de archivos
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

    # Convertir los datos a formato JSON
    datos_json = df.to_dict(orient="records")
    return jsonify({"datos": datos_json})

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

    # Convertir datos a texto para la API de Groq
    datos_texto = json.dumps(datos_json[:5], indent=2)  # Solo los primeros 5 registros para optimizar la consulta

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

# 🔹 Ejecutar la aplicación en modo local
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
