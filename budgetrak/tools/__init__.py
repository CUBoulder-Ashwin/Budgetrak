"""MCP Tools for BudgetTrak"""

from .drive import (
    list_drive_files,
    download_drive_file,
    move_drive_file,
    create_drive_folder,
)

from .parser import (
    parse_bank_statement_from_drive,
    parse_local_pdf,
    categorize_transaction,
)

from .sheets import (
    initialize_budget_sheet,
    save_transactions_to_sheet,
    get_transactions_from_sheet,
    query_transactions,
    get_spending_summary,
)

from .advisor import (
    get_budget_advice,
    identify_savings_opportunities,
    analyze_spending_trends,
    compare_to_budget,
)

__all__ = [
    'list_drive_files',
    'download_drive_file',
    'move_drive_file',
    'create_drive_folder',
    'parse_bank_statement_from_drive',
    'parse_local_pdf',
    'categorize_transaction',
    'initialize_budget_sheet',
    'save_transactions_to_sheet',
    'get_transactions_from_sheet',
    'query_transactions',
    'get_spending_summary',
    'get_budget_advice',
    'identify_savings_opportunities',
    'analyze_spending_trends',
    'compare_to_budget',
]
