#!/bin/bash
# 一键启动开发环境：mock server + 前端
# 用法：在项目根目录运行 bash dev.sh

echo "🚀 启动开发环境..."
echo ""

# 启动 mock server（后台）
echo "📡 启动 Mock Server (port 8001)..."
cd mock-server && node server.js &
MOCK_PID=$!
cd ..

# 等 mock server 启动
sleep 1

# 启动前端
echo "🖥️  启动前端 (port 3000)..."
cd frontend && npx vite --host &
VITE_PID=$!
cd ..

echo ""
echo "✅ 开发环境已启动："
echo "   - Mock Server: http://localhost:8001"
echo "   - Frontend:    http://localhost:3000"
echo ""
echo "按 Ctrl+C 停止所有服务"

# Trap Ctrl+C to kill both
trap "kill $MOCK_PID $VITE_PID 2>/dev/null; echo ''; echo '🛑 已停止所有服务'; exit" INT TERM

# Wait
wait
