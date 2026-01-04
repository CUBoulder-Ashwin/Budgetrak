# 🏦 BudgetTrak

AI-powered budget tracking with automatic bank statement parsing and intelligent financial advice.

**✨ Cross-platform:** Works on Windows, macOS, and Linux!

## 🎯 Features

- 📄 **Automatic PDF Parsing** - Upload bank statements, get structured data
- 🤖 **AI-Powered** - Uses Gemini AI to understand any bank format
- 💬 **Natural Language** - Chat with Claude to manage your budget
- 📊 **Google Sheets** - All data stored in a spreadsheet you control
- 💡 **Smart Advice** - Get personalized budget recommendations
- 🔄 **Multi-Bank** - Works with Chase, Discover, any bank!

## 🚀 Quick Setup

### Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) package manager
- Claude Desktop
- Google Cloud account (for Drive/Sheets API)
- Gemini API key

### 1. Install uv

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Clone & Install
```bash
git clone <your-repo-url>
cd Budgetrak
uv sync
```

### 3. Get API Keys

**Gemini API:**
1. Go to https://aistudio.google.com/apikey
2. Click "Create API Key"
3. Copy the key

**Google OAuth Credentials:**
1. Go to https://console.cloud.google.com/
2. Create a new project (or use existing)
3. Enable **Google Drive API** and **Google Sheets API**
4. Create **OAuth 2.0 Client ID** (Desktop app)
5. Download JSON and save as `budgetrak_credentials.json` in project root

### 4. Configure Environment
```bash
cp .env.example .env
```

Edit `.env` and fill in:
- `GEMINI_API_KEY` - Your Gemini API key
- `BUDGET_SHEET_ID` - (Will add after creating sheet)

### 5. Authenticate & Initialize

**Authenticate with Google:**
```bash
uv run python -c "from budgetrak.utils import get_auth_manager; get_auth_manager().authenticate()"
```
This opens your browser - approve access.

**Create Google Sheet:**
1. Go to https://sheets.google.com
2. Create a new blank sheet
3. Name it "BudgetTrak"
4. Copy the Sheet ID from the URL:
```
   https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID_HERE/edit
```
5. Add it to `.env`:
```
   BUDGET_SHEET_ID=your_sheet_id_here
```

**Initialize the Sheet:**
```bash
uv run python -c "from budgetrak.tools import initialize_budget_sheet; import os; from dotenv import load_dotenv; load_dotenv(); initialize_budget_sheet(os.getenv('BUDGET_SHEET_ID'))"
```

### 6. Configure Claude Desktop

**Find your config file:**

| Platform | Location |
|----------|----------|
| **macOS** | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| **Windows** | `%APPDATA%\Claude\claude_desktop_config.json` |
| **Linux** | `~/.config/Claude/claude_desktop_config.json` |

**Edit the config file:**

**macOS/Linux:**
```json
{
  "mcpServers": {
    "budgettrak": {
      "command": "uv",
      "args": [
        "--directory",
        "/full/path/to/Budgetrak",
        "run",
        "python",
        "run_server.py"
      ]
    }
  }
}
```

**Windows:**
```json
{
  "mcpServers": {
    "budgettrak": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\full\\path\\to\\Budgetrak",
        "run",
        "python",
        "run_server.py"
      ]
    }
  }
}
```

**⚠️ Important:** Replace `/full/path/to/Budgetrak` with your actual project path!

### 7. Restart Claude Desktop

Quit Claude Desktop completely and reopen it.

**Verify it's working:**
- Open Claude Desktop settings
- Check MCP Servers section
- BudgetTrak should show as **connected** ✅

## 💬 Usage Examples

### Parse Bank Statement
```
Upload your December bank statement PDF to Google Drive, then:
"Parse my December statement"
```

Claude will:
1. Find the PDF in your Drive
2. Extract all transactions with Gemini AI
3. Save to your Google Sheet
4. Show you a summary

### Query Spending
```
"How much did I spend on restaurants last month?"
"Show me all Amazon transactions"
"What's my spending by category?"
```

### Get Budget Advice
```
"Give me budget recommendations"
"Where can I save money?"
"Analyze my spending trends"
```

## 🛠️ Manual Testing

Test the server manually:
```bash
# Navigate to project
cd /path/to/Budgetrak

# Run server directly
uv run python run_server.py
```

You should see:
```
🏦 BUDGETTRAK MCP SERVER
✅ All tools registered...
```

Press `Ctrl+C` to stop.

## 📁 Project Structure
```
Budgetrak/
├── budgetrak/                 # Main package
│   ├── server.py             # MCP server
│   ├── tools/                # MCP tools
│   │   ├── drive.py          # Google Drive integration
│   │   ├── parser.py         # PDF parsing with Gemini
│   │   ├── sheets.py         # Google Sheets storage
│   │   └── advisor.py        # Budget recommendations
│   └── utils/                # Utilities
│       ├── google_auth.py    # OAuth handling
│       └── gemini_client.py  # Gemini AI client
├── run_server.py             # Cross-platform launcher ⭐
├── pyproject.toml            # Dependencies
├── .env.example              # Environment template
├── .gitignore                # Git ignore rules
└── README.md
```

## 🔒 Security

**Never commit these files:**
- `.env` - Contains API keys
- `budgetrak_credentials.json` - Google OAuth credentials
- `token.pickle` - Google auth token

They're already in `.gitignore`!

## 🐛 Troubleshooting

### Server won't start

**Check logs:**
```bash
# macOS
tail -50 ~/Library/Logs/Claude/mcp-server-budgettrak.log

# Windows
type %APPDATA%\Claude\logs\mcp-server-budgettrak.log

# Linux
tail -50 ~/.config/Claude/logs/mcp-server-budgettrak.log
```

### "Module not found" errors
```bash
# Reinstall dependencies
uv sync

# Verify installation
uv run python -c "import budgetrak; print('✅ Package installed')"
```

### "uv: command not found"

Add uv to your PATH or use full path in Claude config:

**macOS/Linux:**
```bash
which uv  # Find the path
# Use that path in config
```

**Windows:**
```powershell
where uv  # Find the path
# Use that path in config
```

### Google API errors

**Enable APIs:**
1. Go to https://console.cloud.google.com/
2. Select your project
3. Enable **Google Drive API**
4. Enable **Google Sheets API**

**Re-authenticate:**
```bash
rm token.pickle
uv run python -c "from budgetrak.utils import get_auth_manager; get_auth_manager().authenticate()"
```

## 🎓 How It Works

1. **You upload** a bank statement PDF to Google Drive
2. **You ask Claude** to parse it
3. **Claude calls** the BudgetTrak MCP server
4. **Server downloads** PDF from Drive
5. **Gemini AI** reads and extracts all transactions
6. **Data is saved** to your Google Sheet
7. **Claude responds** with summary and insights

All processing happens locally on your machine!

## 📄 License

MIT License

## 🤝 Contributing

Contributions welcome! Please open an issue first to discuss changes.

## 🙏 Credits

Built with:
- [FastMCP](https://github.com/jlowin/fastmcp) - MCP server framework
- [Google Gemini](https://ai.google.dev/) - AI for PDF parsing & advice
- [uv](https://github.com/astral-sh/uv) - Fast Python package manager
- [Claude Desktop](https://claude.ai/download) - AI assistant interface
