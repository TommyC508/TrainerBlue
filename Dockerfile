FROM python:3.11-slim

WORKDIR /app

# Install system deps (Node.js is required to run the official Pokémon Showdown engine)
RUN apt-get update \
	&& apt-get install -y --no-install-recommends nodejs npm \
	&& rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create directories
RUN mkdir -p data models logs replays

# Run agent
CMD ["python", "src/main.py"]
