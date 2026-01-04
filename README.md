# 🏦 BudgetTrak

AI-powered budget tracking with automatic bank statement parsing and intelligent financial advice.

## ✨ Features

- 📄 **Automatic PDF Parsing** - Upload bank statements, get structured data
- 🤖 **AI-Powered** - Uses Gemini AI to understand any bank format
- 💬 **Natural Language** - Chat with Claude to manage your budget
- 📊 **Google Sheets** - All data stored in a spreadsheet you control
- 💡 **Smart Advice** - Get personalized budget recommendations
- 🔄 **Multi-Bank** - Works with Chase, Discover, any bank!

## 🚀 Quick Setup

### 1. Clone & Install
```bash
git clone <your-repo-url>
cd Budgetrak
uv sync
```

### 2. Get API Keys

**Gemini API:**
1. Go to https://aistudio.google.com/apikey
2. Click "Create API Key"
3. Copy the key

**Google OAuth Credentials:**
1. Go to https://console.cloud.google.com/
2. Create a new project (or use existing)
3. Enable Google Drive API and Google Sheets API
4. Create OAuth 2.0 Client ID (Desktop app)
5. Download JSON as `budgetrak_credentials.json`

### 3. Configure Environment
```bash
cp .env.example .env
nano .env
```

Fill in:
- `GEMINI_API_KEY` - Your Gemini API key
- `BUDGET_SHEET_ID` - Create a Google Sheet and paste its ID

### 4. Authenticate & Initialize
```bash
# Authenticate with Google (opens browser)
uv run python3 -c "from budgetrak.utils import get_auth_manager; get_auth_manager().authenticate()"

# Initialize your Google Sheet
uv run python3 -c "from budgetrak.tools import initialize_budget_sheet; import os; from dotenv import load_dotenv; load_dotenv(); initialize_budget_sheet(os.getenv('BUDGET_SHEET_ID'))"
```

### 5. Configure Claude Desktop

Create/edit `~/Library/Application Support/Claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "budgettrak": {
      "command": "sh",
      "args": [
        "-c",
        "cd /FULL/PATH/TO/Budgetrak && PYTHONPATH=/FULL/PATH/TO/Budgetrak /path/to/.local/bin/uv run python3 budgetrak/server.py"
      ]
    }
  }
}
```

**Replace paths with your actual paths!**

### 6. Restart Claude Desktop

Quit and reopen Claude Desktop. You're ready!

## 💬 Usage

In Claude Desktop, try:
```
Parse my December bank statement
```
```
How much did I spend on restaurants last month?
```
```
Give me budget advice
```

## 🛠️ Development

Run the server manually:
```bash
cd /path/to/Budgetrak
PYTHONPATH=/path/to/Budgetrak uv run python3 budgetrak/server.py
```

## 📁 Project Structure
```
budgetrak/
├── budgetrak/
│   ├── server.py          # Main MCP server
│   ├── tools/             # MCP tools
│   │   ├── drive.py       # Google Drive integration
│   │   ├── parser.py      # PDF parsing
│   │   ├── sheets.py      # Google Sheets storage
│   │   └── advisor.py     # Budget advice
│   └── utils/             # Utilities
│       ├── google_auth.py # OAuth handling
│       └── gemini_client.py # Gemini AI client
├── pyproject.toml         # Dependencies
├── .env.example           # Environment template
└── README.md
```

## 🔒 Security

**Never commit:**
- `.env` - Contains API keys
- `budgetrak_credentials.json` - Google OAuth credentials
- `token.pickle` - Google auth token

These are already in `.gitignore`!

