"""
Gemini AI Client for BudgetTrak

Handles all interactions with Google's Gemini AI:
- PDF parsing and transaction extraction
- Budget analysis and advice
- Category classification
"""

import os
import json
from typing import List, Dict, Any, Optional
from pathlib import Path

import google.generativeai as genai
from PIL import Image
import fitz  # PyMuPDF


class GeminiClient:
    """
    Wrapper for Gemini AI API.
    
    This class provides high-level methods for:
    - Parsing bank statement PDFs
    - Extracting structured transaction data
    - Providing budget advice
    """
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-2.5-flash"):
        """
        Initialize Gemini client.
        
        Args:
            api_key: Gemini API key (or set GEMINI_API_KEY env var)
            model_name: Model to use (default: gemini-2.5-flash)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Gemini API key not found! Set GEMINI_API_KEY environment variable "
                "or pass api_key parameter"
            )
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name)
        print(f"✅ Gemini client initialized with model: {model_name}")
    
    def pdf_to_images(self, pdf_path: str) -> List[Image.Image]:
        """
        Convert PDF pages to PIL images.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of PIL Image objects (one per page)
        """
        print(f"📄 Converting PDF to images: {pdf_path}")
        images = []
        
        # Open PDF
        pdf_document = fitz.open(pdf_path)
        
        # Convert each page to image
        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]
            
            # Render page to image (higher resolution for better OCR)
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for clarity
            
            # Convert to PIL Image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            images.append(img)
            print(f"  ✓ Page {page_num + 1}/{pdf_document.page_count}")
        
        pdf_document.close()
        print(f"✅ Converted {len(images)} pages")
        return images
    
    def parse_bank_statement(self, pdf_path: str) -> Dict[str, Any]:
        """
        Parse a bank statement PDF and extract structured transaction data.
        
        This is the CORE function that uses Gemini Vision to:
        1. Read the PDF as images
        2. Extract account information
        3. Extract all transactions
        4. Categorize each transaction
        5. Return structured JSON
        
        Args:
            pdf_path: Path to bank statement PDF
            
        Returns:
            Dictionary with:
            - account_info: {bank, account_number, period, balances}
            - transactions: List of {date, merchant, amount, category, type}
        """
        print(f"\n🧠 Parsing bank statement with Gemini AI...")
        
        # Convert PDF to images
        images = self.pdf_to_images(pdf_path)
        
        # Create the prompt (this is crucial for good results!)
        prompt = """You are a financial data extraction expert. Analyze this bank statement and extract ALL transactions with perfect accuracy.

**INSTRUCTIONS:**
1. Identify the bank name and account number
2. Find the statement period (start and end dates)
3. Extract beginning and ending balance
4. Extract EVERY transaction (do not skip any!)
5. For each transaction, provide:
   - date: In YYYY-MM-DD format
   - merchant: Clean merchant/description name (remove extra codes)
   - amount: Positive number for debits/purchases, negative for deposits/credits
   - category: Auto-categorize as one of:
     * Income (salary, deposits)
     * Rent/Housing
     * Food/Dining (restaurants, groceries)
     * Transportation (gas, car payments, parking)
     * Shopping (retail, online purchases)
     * Entertainment (movies, subscriptions)
     * Travel (flights, hotels)
     * Bills/Utilities
     * Healthcare
     * Education
     * Transfer (between accounts, Zelle, Venmo)
     * Fees (bank fees, interest)
     * Other
   - type: "debit" or "credit"

**OUTPUT FORMAT:**
Return ONLY valid JSON (no markdown, no explanation). Use this exact structure:

{
    "account_info": {
        "bank": "Bank Name",
        "account_number": "last 4 digits",
        "statement_period_start": "YYYY-MM-DD",
        "statement_period_end": "YYYY-MM-DD",
        "beginning_balance": 0.00,
        "ending_balance": 0.00
    },
    "transactions": [
        {
            "date": "YYYY-MM-DD",
            "merchant": "Merchant Name",
            "amount": 0.00,
            "category": "Category",
            "type": "debit",
            "description": "original description if different from merchant"
        }
    ]
}

**CRITICAL RULES:**
- Be precise with amounts (use actual values from statement)
- Maintain chronological order
- Do not invent or skip transactions
- Clean up merchant names (e.g., "AMZN.COM/BILL" → "Amazon")
- Return ONLY JSON, no other text
"""
        
        # Send to Gemini with all images
        print("  📤 Sending to Gemini AI...")
        response = self.model.generate_content([prompt] + images)
        
        # Parse response
        print("  📥 Processing response...")
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        # Parse JSON
        try:
            data = json.loads(response_text)
            print(f"✅ Parsed {len(data.get('transactions', []))} transactions")
            return data
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON: {e}")
            print(f"Response: {response_text[:500]}...")
            raise
    
    def get_budget_advice(self, transactions: List[Dict], current_balance: float) -> str:
        """
        Analyze transactions and provide budget advice.
        
        Args:
            transactions: List of transaction dictionaries
            current_balance: Current account balance
            
        Returns:
            Budget advice as a formatted string
        """
        print("\n💡 Generating budget advice...")
        
        # Create summary for Gemini
        summary = {
            "current_balance": current_balance,
            "total_transactions": len(transactions),
            "transactions": transactions
        }
        
        prompt = f"""You are a financial advisor. Analyze these transactions and provide personalized budget advice.

Transaction data:
{json.dumps(summary, indent=2)}

Provide advice on:
1. Top spending categories
2. Areas where spending can be reduced
3. Unusual or concerning transactions
4. Budget recommendations
5. Savings opportunities

Be specific, actionable, and encouraging. Format your response in clear sections with bullet points.
"""
        
        response = self.model.generate_content(prompt)
        return response.text


# Singleton instance
_gemini_client: Optional[GeminiClient] = None


def get_gemini_client() -> GeminiClient:
    """
    Get or create singleton Gemini client.
    
    Returns:
        GeminiClient instance
    """
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    return _gemini_client
