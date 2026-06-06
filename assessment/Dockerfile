FROM python:3.11-slim-bookworm

# ffmpeg for audio conversion + libs required by Azure Speech SDK
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libasound2 \
    libssl3 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy as a package so `assessment.app` import path works
COPY . ./assessment/

EXPOSE 8000

CMD ["uvicorn", "assessment.app:app", "--host", "0.0.0.0", "--port", "8000"]
