# 🚀 Quick Start - Docker Deployment

## Prerequisites
- Docker and Docker Compose installed
- OpenRouter API key
- Voyage AI API key

## Setup Steps

### 1. Create `.env` file
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```bash
OPENROUTER_API_KEY=your_actual_key_here
VOYAGEAI_API_KEY=your_actual_key_here
```

### 2. Build and Run
```bash
# Start all services (Qdrant + App)
docker-compose up -d

# View logs
docker-compose logs -f app

# Check status
docker-compose ps
```

### 3. Access the Application
Open your browser to: **http://localhost:8501**

### 4. Stop Services
```bash
docker-compose down

# To also remove volumes (clears all data)
docker-compose down -v
```

## Development Mode (without Docker)

### 1. Install Dependencies
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Start Qdrant
```bash
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

### 3. Run Application
```bash
streamlit run app.py
```

## Troubleshooting

### Qdrant Connection Issues
```bash
# Check if Qdrant is running
docker ps | grep qdrant

# View Qdrant logs
docker logs doc-chat-qdrant
```

### Application Errors
```bash
# View application logs
docker-compose logs -f app

# Restart application
docker-compose restart app
```
