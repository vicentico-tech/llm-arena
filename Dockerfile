FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 GRADIO_SERVER_NAME=0.0.0.0 PORT=7860
RUN useradd -m app
WORKDIR /home/app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY --chown=app:app . .
USER app
EXPOSE 7860
CMD ["python", "app.py"]
