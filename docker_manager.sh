#!/bin/bash
# Docker management script for Mezmur Telegram Bot

case "$1" in
    build)
        echo "Building Docker image..."
        docker build -t mezmur-telegram-bot .
        ;;
    start)
        echo "Starting bot with Docker Compose..."
        docker-compose up -d
        ;;
    stop)
        echo "Stopping bot..."
        docker-compose down
        ;;
    restart)
        echo "Restarting bot..."
        docker-compose restart
        ;;
    logs)
        echo "Showing bot logs..."
        docker-compose logs -f mezmur-bot
        ;;
    status)
        echo "Bot status:"
        docker-compose ps
        ;;
    shell)
        echo "Opening shell in bot container..."
        docker-compose exec mezmur-bot bash
        ;;
    clean)
        echo "Cleaning up Docker resources..."
        docker-compose down
        docker system prune -f
        ;;
    *)
        echo "Usage: $0 {build|start|stop|restart|logs|status|shell|clean}"
        echo ""
        echo "Commands:"
        echo "  build   - Build Docker image"
        echo "  start   - Start bot with Docker Compose"
        echo "  stop    - Stop bot"
        echo "  restart - Restart bot"
        echo "  logs    - Show bot logs"
        echo "  status  - Show bot status"
        echo "  shell   - Open shell in bot container"
        echo "  clean   - Clean up Docker resources"
        exit 1
        ;;
esac
