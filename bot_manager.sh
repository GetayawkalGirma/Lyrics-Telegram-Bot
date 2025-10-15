#!/bin/bash
# Bot management script

BOT_PID_FILE="bot.pid"
BOT_SCRIPT="bot.py"

# Function to check if bot is running
is_bot_running() {
    if [ -f "$BOT_PID_FILE" ]; then
 pid=$(cat "$BOT_PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            # Check if this is actually our bot process
            if ps -p "$pid" -o command= | grep -q "python.*$BOT_SCRIPT"; then
                return 0  # Bot is running
            else
                # PID file exists but process is not our bot, clean it up
                rm -f "$BOT_PID_FILE"
            fi
        else
            # PID file exists but process is dead, clean it up
            rm -f "$BOT_PID_FILE"
        fi
    fi
    
    # Also check for any python bot.py processes
    if pgrep -f "python.*$BOT_SCRIPT" > /dev/null; then
        return 0  # Bot is running
    fi
    
    return 1  # Bot is not running
}

# Function to get bot PID
get_bot_pid() {
    if [ -f "$BOT_PID_FILE" ]; then
        cat "$BOT_PID_FILE"
    else
        pgrep -f "python.*$BOT_SCRIPT" | head -1
    fi
}

# Function to cleanup stale processes
cleanup_stale_processes() {
    echo "Cleaning up any stale bot processes..."
    pkill -f "python.*$BOT_SCRIPT" 2>/dev/null || true
    sleep 1
    pkill -9 -f "python.*$BOT_SCRIPT" 2>/dev/null || true
    rm -f "$BOT_PID_FILE"
}

case "$1" in
    start)
        echo "Checking for existing bot processes..."
        if is_bot_running; then
 pid=$(get_bot_pid)
            echo "❌ Bot is already running with PID: $pid"
            echo "Use './bot_manager.sh stop' to stop it first, or './bot_manager.sh restart' to restart it."
            exit 1
        fi
        
        echo "Starting bot..."
        source venv/bin/activate
        
        # Start bot in background and save PID
        nohup python "$BOT_SCRIPT" > bot.log 2>&1 &
        bot_pid=$!
        echo "$bot_pid" > "$BOT_PID_FILE"
        
        # Give it a moment to start
        sleep 2
        
        # Verify it's still running
        if ps -p "$bot_pid" > /dev/null 2>&1; then
            echo "✅ Bot started successfully with PID: $bot_pid"
            echo "📝 Logs are being written to: bot.log"
            echo "🛑 Use './bot_manager.sh stop' to stop the bot"
        else
            echo "❌ Failed to start bot. Check bot.log for errors."
            rm -f "$BOT_PID_FILE"
            exit 1
        fi
        ;;
    stop)
        echo "Stopping bot..."
        if is_bot_running; then
 pid=$(get_bot_pid)
            echo "Stopping bot with PID: $pid"
            kill "$pid" 2>/dev/null || true
            sleep 2
            
            # Force kill if still running
            if ps -p "$pid" > /dev/null 2>&1; then
                echo "Force killing bot..."
                kill -9 "$pid" 2>/dev/null || true
            fi
            
            # Clean up any remaining processes
            cleanup_stale_processes
            echo "✅ Bot stopped."
        else
            echo "Bot is not running."
            cleanup_stale_processes
        fi
        ;;
    restart)
        echo "Restarting bot..."
        if is_bot_running; then
 pid=$(get_bot_pid)
            echo "Stopping bot with PID: $pid"
            kill "$pid" 2>/dev/null || true
            sleep 2
            cleanup_stale_processes
        fi
        
        echo "Starting bot..."
        source venv/bin/activate
        nohup python "$BOT_SCRIPT" > bot.log 2>&1 &
 bot_pid=$!
        echo "$bot_pid" > "$BOT_PID_FILE"
        sleep 2
        
        if ps -p "$bot_pid" > /dev/null 2>&1; then
            echo "✅ Bot restarted successfully with PID: $bot_pid"
        else
            echo "❌ Failed to restart bot. Check bot.log for errors."
            rm -f "$BOT_PID_FILE"
            exit 1
        fi
        ;;
    status)
        if is_bot_running; then
 pid=$(get_bot_pid)
            echo "✅ Bot is running with PID: $pid"
            echo "📊 Process info:"
            ps -p "$pid" -o pid,ppid,etime,pcpu,pmem,command
            echo ""
            echo "📝 Recent logs (last 10 lines):"
            if [ -f "bot.log" ]; then
                tail -10 bot.log
            else
                echo "No log file found."
            fi
        else
            echo "❌ Bot is not running"
            cleanup_stale_processes
        fi
        ;;
    logs)
        if [ -f "bot.log" ]; then
            echo "📝 Bot logs (last 50 lines):"
            tail -50 bot.log
        else
            echo "No log file found."
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the bot (prevents multiple instances)"
        echo "  stop    - Stop the bot"
        echo "  restart - Restart the bot"
        echo "  status  - Show bot status and process info"
        echo "  logs    - Show recent bot logs"
        exit 1
        ;;
esac
