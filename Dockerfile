FROM python:3.12-slim

WORKDIR /app

# Install uv for faster dependency installation
RUN pip install uv

# Copy only requirements file first (for better caching)
COPY requirements.txt ./

# Install dependencies
RUN uv pip install -r requirements.txt --system

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p /app/faiss_index /app/resources /app/books /app/scripts /app/utils

# Default command
CMD ["sh", "-c", "python scripts/init_rag.py && python server.py"]