FROM python:3.10-slim

WORKDIR /app

COPY frontend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY frontend/streamlit_app.py .
COPY frontend/.env .env

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]