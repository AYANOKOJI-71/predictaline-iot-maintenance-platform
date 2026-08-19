FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml ./
COPY apps/api/src ./apps/api/src

RUN pip install --no-cache-dir .

EXPOSE 8000

CMD ["uvicorn", "predictaline.main:app", "--host", "0.0.0.0", "--port", "8000"]
