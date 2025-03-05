# Usa una imagen de Python
FROM python:3.13

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos del proyecto al contenedor
COPY . .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exporta la variable de entorno para que el contenedor la use
ENV GROQ_API_KEY=${GROQ_API_KEY}

# Define el comando para ejecutar la aplicación
CMD ["python", "chat.py"]
