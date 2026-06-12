#!/bin/bash
# Quick start script for Africa Cyber Trust Infrastructure

echo "🚀 Starting Africa Cyber Trust Infrastructure..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Start Docker services
echo "📦 Starting PostgreSQL and Redis..."
cd docker
docker-compose up -d
cd ..

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 5

# Check if services are running
if docker-compose -f docker/docker-compose.yml ps | grep -q "Up"; then
    echo "✅ Infrastructure services started successfully"
else
    echo "❌ Failed to start infrastructure services"
    exit 1
fi

echo ""
echo "🎉 Infrastructure is ready!"
echo ""
echo "Next steps:"
echo "1. Open a new terminal and run the backend:"
echo "   cd backend"
echo "   source venv/bin/activate  # or venv\\Scripts\\activate on Windows"
echo "   uvicorn app.main:app --reload"
echo ""
echo "2. Open another terminal and run the frontend:"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "3. Access the application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "To stop services: cd docker && docker-compose down"
