FROM python:3.11-slim

WORKDIR /app

# Install system deps (Node.js is required to run the official Pokémon Showdown engine)
RUN apt-get update \
	&& apt-get install -y --no-install-recommends bash nodejs npm \
	&& rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Ensure Showdown submodule content is present and build simulator tools
RUN test -f external/pokemon-showdown/package.json || (echo "Missing external/pokemon-showdown submodule files. Run: git submodule update --init --recursive" && false)
RUN bash scripts/setup_showdown.sh

# Create runtime directories
RUN mkdir -p data models logs replays

# Run agent
CMD ["python", "src/main.py"]
