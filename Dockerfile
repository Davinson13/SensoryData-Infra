FROM python:3.9
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
ENV GROQ_API_KEY=${GROQ_API_KEY}
CMD ["python", "chat.py"]
