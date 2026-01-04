import os
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..utils import get_sheets_service


def get_sheet_id_from_env() -> str:
    sheet_id = os.getenv("BUDGET_SHEET_ID")
    if not sheet_id:
        raise ValueError(
            "BUDGET_SHEET_ID not set in environment! "
            "Please create a Google Sheet and add its ID to .env"
        )
    return sheet_id


def initialize_budget_sheet(sheet_id: str) -> Dict:

    print(f"📊 Initializing budget sheet: {sheet_id}")
    
    service = get_sheets_service()
    
    # Get existing sheet info
    spreadsheet = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
    print(f"  Sheet name: {spreadsheet['properties']['title']}")
    
    # Create Transactions sheet if doesn't exist
    sheets = spreadsheet.get('sheets', [])
    has_transactions = any(s['properties']['title'] == 'Transactions' for s in sheets)
    
    if not has_transactions:
        print("  Creating Transactions sheet...")
        requests = [{
            'addSheet': {
                'properties': {
                    'title': 'Transactions',
                    'gridProperties': {
                        'frozenRowCount': 1  # Freeze header row
                    }
                }
            }
        }]
        service.spreadsheets().batchUpdate(
            spreadsheetId=sheet_id,
            body={'requests': requests}
        ).execute()
    
    # Write headers
    headers = [
        ['Date', 'Merchant', 'Amount', 'Category', 'Type', 'Bank', 'Account', 'Notes']
    ]
    
    service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range='Transactions!A1:H1',
        valueInputOption='RAW',
        body={'values': headers}
    ).execute()
    
    print("✅ Sheet initialized")
    return spreadsheet


def save_transactions_to_sheet(
    transactions: List[Dict[str, Any]],
    account_info: Dict[str, Any],
    sheet_id: Optional[str] = None
) -> Dict:

    print(f"\n📊 Saving {len(transactions)} transactions to Google Sheets...")
    
    if sheet_id is None:
        sheet_id = get_sheet_id_from_env()
    
    service = get_sheets_service()
    
    # Format transactions for sheets
    rows = []
    for t in transactions:
        row = [
            t.get('date', ''),
            t.get('merchant', ''),
            t.get('amount', 0),
            t.get('category', ''),
            t.get('type', ''),
            account_info.get('bank', ''),
            account_info.get('account_number', ''),
            t.get('description', '')  # Notes
        ]
        rows.append(row)
    
    # Append to sheet
    result = service.spreadsheets().values().append(
        spreadsheetId=sheet_id,
        range='Transactions!A:H',
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body={'values': rows}
    ).execute()
    
    print(f"✅ Added {len(rows)} rows to sheet")
    print(f"  Updated range: {result['updates']['updatedRange']}")
    
    return result


def get_transactions_from_sheet(
    sheet_id: Optional[str] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:

    print(f"📖 Reading transactions from Google Sheets...")
    
    if sheet_id is None:
        sheet_id = get_sheet_id_from_env()
    
    service = get_sheets_service()
    
    # Read all data
    result = service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range='Transactions!A2:H'  # Skip header
    ).execute()
    
    values = result.get('values', [])
    
    # Convert to dictionaries
    transactions = []
    for row in values[-limit:]:  # Get last N rows
        if len(row) >= 5:  # Minimum required columns
            transactions.append({
                'date': row[0],
                'merchant': row[1],
                'amount': float(row[2]) if row[2] else 0,
                'category': row[3],
                'type': row[4],
                'bank': row[5] if len(row) > 5 else '',
                'account': row[6] if len(row) > 6 else '',
                'notes': row[7] if len(row) > 7 else ''
            })
    
    print(f"✅ Retrieved {len(transactions)} transactions")
    return transactions


def query_transactions(
    category: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    merchant: Optional[str] = None,
    sheet_id: Optional[str] = None
) -> List[Dict[str, Any]]:

    print(f"🔍 Querying transactions...")
    print(f"  Filters: category={category}, dates={start_date} to {end_date}, merchant={merchant}")
    
    # Get all transactions
    all_transactions = get_transactions_from_sheet(sheet_id=sheet_id, limit=1000)
    
    # Apply filters
    filtered = all_transactions
    
    if category:
        filtered = [t for t in filtered if t['category'].lower() == category.lower()]
    
    if start_date:
        filtered = [t for t in filtered if t['date'] >= start_date]
    
    if end_date:
        filtered = [t for t in filtered if t['date'] <= end_date]
    
    if merchant:
        filtered = [t for t in filtered 
                   if merchant.lower() in t['merchant'].lower()]
    
    print(f"✅ Found {len(filtered)} matching transactions")
    return filtered


def get_spending_summary(
    sheet_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Dict[str, Any]:

    print(f"📈 Generating spending summary...")
    
    transactions = get_transactions_from_sheet(sheet_id=sheet_id, limit=1000)
    
    # Filter by date if provided
    if start_date:
        transactions = [t for t in transactions if t['date'] >= start_date]
    if end_date:
        transactions = [t for t in transactions if t['date'] <= end_date]
    
    # Calculate totals by category
    category_totals = {}
    total_spent = 0
    total_income = 0
    
    for t in transactions:
        category = t['category']
        amount = t['amount']
        
        if category not in category_totals:
            category_totals[category] = 0
        
        category_totals[category] += amount
        
        if amount > 0:
            total_spent += amount
        else:
            total_income += abs(amount)
    
    summary = {
        'total_spent': total_spent,
        'total_income': total_income,
        'net': total_income - total_spent,
        'by_category': category_totals,
        'transaction_count': len(transactions)
    }
    
    print(f"✅ Summary generated: {len(category_totals)} categories")
    return summary
