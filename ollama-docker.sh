#!/bin/bash

# Ollama Docker Management Script

case "$1" in
    start)
        echo "🚀 Starting Ollama via Docker..."
        docker-compose up -d ollama
        echo "⏳ Waiting for Ollama to be ready..."
        sleep 5
        
        # Check if Ollama is responding
        for i in {1..30}; do
            if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
                echo "✅ Ollama is ready!"
                echo "📋 Available models:"
                curl -s http://localhost:11434/api/tags | jq -r '.models[].name' 2>/dev/null || echo "No models installed yet"
                break
            fi
            echo "⏳ Waiting for Ollama... ($i/30)"
            sleep 2
        done
        ;;
    stop)
        echo "🛑 Stopping Ollama..."
        docker-compose down
        ;;
    status)
        echo "📊 Ollama Status:"
        if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
            echo "✅ Ollama is running"
            echo "📋 Available models:"
            curl -s http://localhost:11434/api/tags | jq -r '.models[].name' 2>/dev/null || echo "No models installed"
        else
            echo "❌ Ollama is not running"
        fi
        ;;
    pull)
        if [ -z "$2" ]; then
            echo "Usage: $0 pull <model_name>"
            echo "Example: $0 pull llama3.2:3b"
            exit 1
        fi
        echo "📥 Pulling model: $2"
        docker exec ollama ollama pull "$2"
        ;;
    logs)
        echo "📋 Ollama logs:"
        docker-compose logs -f ollama
        ;;
    *)
        echo "Usage: $0 {start|stop|status|pull|logs}"
        echo ""
        echo "Commands:"
        echo "  start    - Start Ollama via Docker"
        echo "  stop     - Stop Ollama"
        echo "  status   - Check if Ollama is running and list models"
        echo "  pull     - Pull a model (e.g., 'pull llama3.2:3b')"
        echo "  logs     - Show Ollama logs"
        echo ""
        echo "Examples:"
        echo "  $0 start"
        echo "  $0 pull llama3.2:3b"
        echo "  $0 status"
        exit 1
        ;;
esac
