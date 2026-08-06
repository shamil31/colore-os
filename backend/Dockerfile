FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y gcc && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Diagnostic only: lets the running container report which code it was built
# from. See app/core/startup.py.
ARG GIT_COMMIT=unknown
ARG BUILD_CONTEXT=unknown
ENV GIT_COMMIT=${GIT_COMMIT}
ENV BUILD_CONTEXT=${BUILD_CONTEXT}

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]