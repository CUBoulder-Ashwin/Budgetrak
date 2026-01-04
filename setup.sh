#!/bin/bash
# Quick setup script for macOS/Linux

echo "🚀 Setting up BudgetTrak..."

# Install dependencies
echo "📦 Installing dependencies..."
uv sync

# Check for credentials
if [ ! -f "budgetrak_credentials.json" ]; then
    echo "⚠️  budgetrak_credentials.json not found!"
    echo "   Download OAuth credentials from Google Cloud Console"
    exit 1
fi

# Check for .env
if [ ! -f ".env" ]; then
    echo "📝 Creating .env from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your API keys!"
    exit 1
fi

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your API keys"
echo "2. Run: uv run python -c \"from budgetrak.utils import get_auth_manager; get_auth_manager().authenticate()\""
echo "3. Configure Claude Desktop (see README.md)"
