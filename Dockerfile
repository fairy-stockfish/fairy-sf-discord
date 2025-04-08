FROM python:3.11-slim

# Install build dependencies
RUN apt-get update && apt-get install -y \
    g++ make cmake git \
    && rm -rf /var/lib/apt/lists/*

# Build Fairy-Stockfish
WORKDIR /build
RUN git clone https://github.com/ianfab/Fairy-Stockfish.git
WORKDIR /build/Fairy-Stockfish/src
RUN make build largeboards=yes all=yes

# App setup
WORKDIR /app
COPY bot.py .
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN cp /build/Fairy-Stockfish/src/stockfish /app/fairy-stockfish

EXPOSE 10000
CMD ["python", "bot.py"]
