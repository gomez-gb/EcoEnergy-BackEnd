FROM python:3.14-slim

WORKDIR /app

# Copiar solo requirements primero: si el código cambia pero las
# dependencias no, Docker reutiliza esta capa cacheada y no reinstala nada.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
