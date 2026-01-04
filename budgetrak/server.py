"""
BudgetTrak MCP Server

This is the main entry point for the BudgetTrak MCP server.
It registers all tools with FastMCP and handles communication with Claude Desktop.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load environment variables
load_dotenv()

# Import all our tools
from budgetrak.tools import (
    # Drive tools
    list_drive_files,
    move_drive_file,
    create_drive_folder,
    # Parser tools
    parse_bank_statement_from_drive,
    parse_local_pdf,
    categorize_transaction,
    # Sheets tools
    initialize_budget_sheet,
    save_transactions_to_sheet,
    get_transactions_from_sheet,
    query_transactions,
    get_spending_summary,
    # Advisor tools
    get_budget_advice,
    identify_savings_opportunities,
    analyze_spending_trends,
)

# Create FastMCP server
mcp = FastMCP("BudgetTrak")

print("🚀 Starting BudgetTrak MCP Server...")
print(f"📁 Working directory: {os.getcwd()}")


# ============================================================================
# REGISTER GOOGLE DRIVE TOOLS
# ============================================================================

@mcp.tool()
def search_drive_files(query: str, max_results: int = 20):
    """
    Search for files in Google Drive.
    
    Use this to find bank statements, receipts, or other financial documents.
    
    Args:
        query: Search term (e.g., "December Chase" or "bank statement")
        max_results: Maximum number of results to return (default: 20)
        
    Returns:
        List of files with id, name, and metadata
        
    Example usage:
        "Find my December Discover statement"
        → search_drive_files("December Discover")
    """
    return list_drive_files(query=query, max_results=max_results)


@mcp.tool()
def move_file_to_folder(file_id: str, folder_id: str):
    """
    Move a file to a different folder in Google Drive.
    
    Useful for organizing processed statements.
    
    Args:
        file_id: ID of the file to move
        folder_id: ID of the destination folder
        
    Returns:
        Updated file metadata
    """
    return move_drive_file(file_id, folder_id)


@mcp.tool()
def create_folder(name: str, parent_folder_id: Optional[str] = None):
    """
    Create a new folder in Google Drive.
    
    Args:
        name: Name of the new folder
        parent_folder_id: Parent folder ID (optional)
        
    Returns:
        Created folder metadata with ID
    """
    return create_drive_folder(name, parent_folder_id)


# ============================================================================
# REGISTER PARSER TOOLS
# ============================================================================

@mcp.tool()
def parse_statement(file_id: str):
    """
    Parse a bank statement PDF and extract all transactions.
    
    This is the MAIN parsing tool! It:
    1. Downloads the PDF from Google Drive
    2. Uses Gemini AI to extract transactions
    3. Returns structured data (account info + transactions)
    
    Args:
        file_id: Google Drive file ID of the bank statement PDF
        
    Returns:
        Dictionary with:
        - account_info: Bank name, account number, balances, period
        - transactions: List of all transactions (date, merchant, amount, category)
        
    Example usage:
        "Parse my December Chase statement"
        1. search_drive_files("December Chase") → get file_id
        2. parse_statement(file_id) → get transactions
        3. save_transactions(...) → store in Google Sheets
    """
    return parse_bank_statement_from_drive(file_id)


@mcp.tool()
def recategorize_transaction(description: str, amount: float):
    """
    Categorize or re-categorize a single transaction.
    
    Args:
        description: Transaction description
        amount: Transaction amount
        
    Returns:
        Suggested category name
    """
    return categorize_transaction(description, amount)


# ============================================================================
# REGISTER GOOGLE SHEETS TOOLS
# ============================================================================

@mcp.tool()
def setup_budget_sheet(sheet_id: str):
    """
    Initialize a Google Sheet for budget tracking.
    
    Creates proper headers and formatting.
    
    Args:
        sheet_id: Google Sheets document ID
        
    Returns:
        Sheet metadata
        
    Example usage:
        "Set up my budget sheet"
        User provides sheet ID → setup_budget_sheet(sheet_id)
    """
    return initialize_budget_sheet(sheet_id)


@mcp.tool()
def save_transactions(
    transactions: list,
    account_info: dict,
    sheet_id: Optional[str] = None
):
    """
    Save parsed transactions to Google Sheets.
    
    Call this after parse_statement to store the data.
    
    Args:
        transactions: List of transaction dictionaries
        account_info: Account metadata (bank, account number, etc.)
        sheet_id: Google Sheets ID (optional, uses env var if not provided)
        
    Returns:
        Result with number of rows added
        
    Example workflow:
        1. parse_statement(file_id) → get data
        2. save_transactions(data['transactions'], data['account_info'])
    """
    return save_transactions_to_sheet(transactions, account_info, sheet_id)


@mcp.tool()
def get_recent_transactions(limit: int = 50, sheet_id: Optional[str] = None):
    """
    Get recent transactions from Google Sheets.
    
    Args:
        limit: Maximum number of transactions to return (default: 50)
        sheet_id: Google Sheets ID (optional)
        
    Returns:
        List of recent transactions
        
    Example usage:
        "Show me my last 10 transactions"
        → get_recent_transactions(limit=10)
    """
    return get_transactions_from_sheet(sheet_id=sheet_id, limit=limit)


@mcp.tool()
def search_transactions(
    category: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    merchant: Optional[str] = None,
    sheet_id: Optional[str] = None
):
    """
    Search transactions with filters.
    
    Args:
        category: Filter by category (e.g., "Food/Dining")
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        merchant: Merchant name (partial match)
        sheet_id: Google Sheets ID (optional)
        
    Returns:
        List of matching transactions
        
    Example usage:
        "How much did I spend on food last month?"
        → search_transactions(
            category="Food/Dining",
            start_date="2025-12-01",
            end_date="2025-12-31"
          )
        
        "Show me all Amazon transactions"
        → search_transactions(merchant="Amazon")
    """
    return query_transactions(
        category=category,
        start_date=start_date,
        end_date=end_date,
        merchant=merchant,
        sheet_id=sheet_id
    )


@mcp.tool()
def get_spending_summary_by_category(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    sheet_id: Optional[str] = None
):
    """
    Get spending summary broken down by category.
    
    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        sheet_id: Google Sheets ID (optional)
        
    Returns:
        Dictionary with total spent, income, and spending by category
        
    Example usage:
        "What's my spending summary for December?"
        → get_spending_summary_by_category(
            start_date="2025-12-01",
            end_date="2025-12-31"
          )
    """
    return get_spending_summary(
        sheet_id=sheet_id,
        start_date=start_date,
        end_date=end_date
    )


# ============================================================================
# REGISTER BUDGET ADVISOR TOOLS
# ============================================================================

@mcp.tool()
def get_budget_recommendations(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    sheet_id: Optional[str] = None
):
    """
    Get personalized budget advice based on spending patterns.
    
    Uses AI to analyze your transactions and provide:
    - Spending insights
    - Areas to reduce costs
    - Budget recommendations
    - Savings opportunities
    
    Args:
        start_date: Start date for analysis (YYYY-MM-DD)
        end_date: End date for analysis (YYYY-MM-DD)
        sheet_id: Google Sheets ID (optional)
        
    Returns:
        Formatted budget advice text
        
    Example usage:
        "Give me some budget advice"
        → get_budget_recommendations()
        
        "How can I save money based on last month's spending?"
        → get_budget_recommendations(
            start_date="2025-11-01",
            end_date="2025-11-30"
          )
    """
    return get_budget_advice(
        sheet_id=sheet_id,
        start_date=start_date,
        end_date=end_date
    )


@mcp.tool()
def find_savings_opportunities(sheet_id: Optional[str] = None):
    """
    Identify specific ways to save money.
    
    Analyzes transactions to find:
    - Unused subscriptions
    - High spending categories
    - Duplicate charges
    - Areas to cut costs
    
    Args:
        sheet_id: Google Sheets ID (optional)
        
    Returns:
        Formatted list of savings opportunities
        
    Example usage:
        "Where can I save money?"
        → find_savings_opportunities()
    """
    return identify_savings_opportunities(sheet_id=sheet_id)


@mcp.tool()
def analyze_trends(
    category: Optional[str] = None,
    sheet_id: Optional[str] = None
):
    """
    Analyze spending trends over time.
    
    Args:
        category: Specific category to analyze (or all categories if None)
        sheet_id: Google Sheets ID (optional)
        
    Returns:
        Trend analysis with insights and predictions
        
    Example usage:
        "How is my food spending trending?"
        → analyze_trends(category="Food/Dining")
        
        "Analyze my overall spending trends"
        → analyze_trends()
    """
    return analyze_spending_trends(category=category, sheet_id=sheet_id)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point for the MCP server."""
    print("\n" + "="*60)
    print("🏦 BUDGETTRAK MCP SERVER")
    print("="*60)
    print("\n✅ All tools registered:")
    print("  📁 Drive: search_drive_files, move_file_to_folder, create_folder")
    print("  🔍 Parser: parse_statement, recategorize_transaction")
    print("  📊 Sheets: setup_budget_sheet, save_transactions, get_recent_transactions,")
    print("           search_transactions, get_spending_summary_by_category")
    print("  💡 Advisor: get_budget_recommendations, find_savings_opportunities, analyze_trends")
    print("\n🎯 Ready to accept requests from Claude Desktop!")
    print("="*60 + "\n")
    
    # Run the MCP server
    mcp.run()


if __name__ == "__main__":
    main()
