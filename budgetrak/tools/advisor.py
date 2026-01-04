from typing import List, Dict, Any, Optional

from ..utils import get_gemini_client
from .sheets import get_transactions_from_sheet, get_spending_summary


def get_budget_advice(
    sheet_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> str:

    print(f"\n💡 Generating budget advice...")
    
    # Get transaction data
    transactions = get_transactions_from_sheet(sheet_id=sheet_id, limit=200)
    summary = get_spending_summary(
        sheet_id=sheet_id,
        start_date=start_date,
        end_date=end_date
    )
    
    # Get current balance (from most recent transaction's ending balance)
    # For now, we'll calculate from transactions
    if transactions:
        # Assuming we have income/expense, calculate rough balance
        current_balance = summary['total_income'] - summary['total_spent']
    else:
        current_balance = 0
    
    # Use Gemini for advice
    gemini = get_gemini_client()
    advice = gemini.get_budget_advice(transactions, current_balance)
    
    return advice


def identify_savings_opportunities(sheet_id: Optional[str] = None) -> str:

    print(f"\n💰 Identifying savings opportunities...")
    
    transactions = get_transactions_from_sheet(sheet_id=sheet_id, limit=500)
    summary = get_spending_summary(sheet_id=sheet_id)
    
    gemini = get_gemini_client()
    
    prompt = f"""You are a financial advisor analyzing transactions to find savings opportunities.

Transaction Summary:
- Total transactions: {len(transactions)}
- Total spent: ${summary['total_spent']:.2f}
- Total income: ${summary['total_income']:.2f}
- Net: ${summary['net']:.2f}

Spending by category:
{chr(10).join(f"- {cat}: ${amt:.2f}" for cat, amt in summary['by_category'].items())}

Recent transactions (last 20):
{chr(10).join(f"- {t['date']}: {t['merchant']} (${t['amount']:.2f}) - {t['category']}" for t in transactions[-20:])}

Identify specific savings opportunities:
1. Subscriptions that might be unused or unnecessary
2. Categories with excessive spending
3. Recurring charges that could be reduced
4. Duplicate or suspicious charges
5. Alternative cheaper options

Be specific and actionable. Format as a numbered list with dollar amounts where possible.
"""
    
    response = gemini.model.generate_content(prompt)
    return response.text


def analyze_spending_trends(
    category: Optional[str] = None,
    sheet_id: Optional[str] = None
) -> str:

    print(f"\n📊 Analyzing spending trends{f' for {category}' if category else ''}...")
    
    transactions = get_transactions_from_sheet(sheet_id=sheet_id, limit=1000)
    
    # Filter by category if specified
    if category:
        transactions = [t for t in transactions 
                       if t['category'].lower() == category.lower()]
    
    # Group by month
    monthly_spending = {}
    for t in transactions:
        # Extract month from date (assuming YYYY-MM-DD format)
        month = t['date'][:7]  # YYYY-MM
        if month not in monthly_spending:
            monthly_spending[month] = 0
        monthly_spending[month] += t['amount']
    
    gemini = get_gemini_client()
    
    prompt = f"""Analyze these spending trends and provide insights:

Category: {category if category else "All Categories"}

Monthly spending:
{chr(10).join(f"- {month}: ${amount:.2f}" for month, amount in sorted(monthly_spending.items()))}

Provide:
1. Overall trend (increasing/decreasing/stable)
2. Seasonal patterns if any
3. Months with unusual spending
4. Predictions for next month
5. Recommendations

Be concise and actionable.
"""
    
    response = gemini.model.generate_content(prompt)
    return response.text


def compare_to_budget(
    budget_targets: Dict[str, float],
    sheet_id: Optional[str] = None
) -> str:

    print(f"\n🎯 Comparing spending to budget targets...")
    
    summary = get_spending_summary(sheet_id=sheet_id)
    actual = summary['by_category']
    
    comparison = {}
    for category, target in budget_targets.items():
        actual_amount = actual.get(category, 0)
        difference = actual_amount - target
        percentage = (actual_amount / target * 100) if target > 0 else 0
        
        comparison[category] = {
            'target': target,
            'actual': actual_amount,
            'difference': difference,
            'percentage': percentage
        }
    
    # Format report
    report = "## Budget vs Actual Spending\n\n"
    
    for category, data in comparison.items():
        status = "🟢" if data['difference'] <= 0 else "🔴"
        report += f"{status} **{category}**\n"
        report += f"  - Target: ${data['target']:.2f}\n"
        report += f"  - Actual: ${data['actual']:.2f}\n"
        report += f"  - Difference: ${data['difference']:+.2f} ({data['percentage']:.1f}%)\n\n"
    
    return report
