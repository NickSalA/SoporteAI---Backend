# -------- Stage 1: Build --------
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Paquetes SOLO para compilar wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/*

# Cache eficiente: primero requirements
COPY requirements.txt /app/requirements.txt

# Instala dependencias en un prefix aislado para copiar luego
RUN python -m pip install --upgrade pip setuptools wheel \
 && python -m pip install --no-cache-dir --prefix=/install -r /app/requirements.txt

# Copia el código fuente
COPY . /app

# -------- Stage 2: Runtime --------
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Solo librerías de RUNTIME (sin toolchains)
# Nota: libpq5 provee el cliente de Postgres necesario en ejecución
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
 && rm -rf /var/lib/apt/lists/*

# Copia las libs de Python ya instaladas (del builder)
COPY --from=builder /install /usr/local

# Copia el código (último para mejor cache)
COPY --from=builder /app /app

# Usuario no root
RUN useradd --create-home appuser || true \
 && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
