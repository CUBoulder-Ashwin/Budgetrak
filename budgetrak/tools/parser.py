"""
PDF Parser Tools for MCP

These tools handle parsing bank statements using Gemini AI.
"""

import os
import tempfile
from typing import Dict, Any

from ..utils import get_gemini_client
from .drive import download_drive_file


def parse_bank_statement_from_drive(file_id: str) -> Dict[str, Any]:

    print(f"\n{'='*60}")
    print(f"🏦 PARSING BANK STATEMENT")
    print(f"{'='*60}")
    
    # Create temp directory for download
    with tempfile.TemporaryDirectory() as temp_dir:
        pdf_path = os.path.join(temp_dir, "statement.pdf")
        
        # Step 1: Download from Drive
        print("\n[1/2] Downloading from Google Drive...")
        download_drive_file(file_id, pdf_path)
        
        # Step 2: Parse with Gemini
        print("\n[2/2] Extracting transactions with Gemini AI...")
        gemini = get_gemini_client()
        result = gemini.parse_bank_statement(pdf_path)
        
        print(f"\n{'='*60}")
        print(f"✅ PARSING COMPLETE")
        print(f"{'='*60}")
        print(f"Bank: {result['account_info']['bank']}")
        print(f"Account: ...{result['account_info']['account_number']}")
        print(f"Period: {result['account_info']['statement_period_start']} to {result['account_info']['statement_period_end']}")
        print(f"Transactions: {len(result['transactions'])}")
        print(f"Beginning Balance: ${result['account_info']['beginning_balance']:.2f}")
        print(f"Ending Balance: ${result['account_info']['ending_balance']:.2f}")
        
        return result


def parse_local_pdf(pdf_path: str) -> Dict[str, Any]:

    print(f"\n🏦 Parsing local PDF: {pdf_path}")
    
    gemini = get_gemini_client()
    result = gemini.parse_bank_statement(pdf_path)
    
    print(f"✅ Parsed {len(result['transactions'])} transactions")
    return result


def categorize_transaction(description: str, amount: float) -> str:

    gemini = get_gemini_client()
    
    prompt = f"""Categorize this transaction into ONE of these categories:
- Income
- Rent/Housing
- Food/Dining
- Transportation
- Shopping
- Entertainment
- Travel
- Bills/Utilities
- Healthcare
- Education
- Transfer
- Fees
- Other

Transaction: {description}
Amount: ${amount}

Respond with ONLY the category name, nothing else.
"""
    
    response = gemini.model.generate_content(prompt)
    category = response.text.strip()
    
    return category
