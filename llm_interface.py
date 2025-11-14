# llm_interface.py (Cloud-ready, explicit schema + strict system prompt)
import os
from huggingface_hub import InferenceClient

HF_MODEL_ID = "meta-llama/Meta-Llama-3-8B-Instruct"

_SCHEMA = """
Database: InsightMart (SQLite)
Tables and columns (use these exact names):

Products(
    ProductID,
    ProductName,
    Category,
    Brand,
    UnitPrice,
    CostPrice,
    StockQty,
    ReorderLevel,
    CreatedDate,
    IsActive
)

Customers(
    CustomerID,
    Name,
    Gender,
    Age,
    City,
    JoinDate,
    LoyaltyPoints,
    IsActive
)

Stores(
    StoreID,
    StoreName,
    City,
    ManagerName,
    CreatedDate,
    IsActive
)

Sales(
    SaleID,
    SaleDate,
    CustomerID,
    IsGuestCustomer,
    TotalAmount,
    StoreID,
    IsActive
)

SalesDetails(
    SaleDetailID,
    SaleID,
    ProductID,
    ProductName,
    Quantity,
    UnitPrice,
    TempUnitPrice,
    Discount,
    SubTotal
)

SalesPayments(
    PaymentID,
    SaleID,
    PaymentMethod,
    Amount
)

Purchases(
    PurchaseID,
    SupplierID,
    PurchaseDate,
    TotalCost,
    PaymentStatus,
    StoreID,
    IsActive
)

PurchaseDetails(
    PurchaseDetailID,
    PurchaseID,
    ProductID,
    Quantity,
    UnitCost,
    SubTotal
)

Suppliers(
    SupplierID,
    SupplierName,
    Contact,
    City,
    Rating,
    IsActive
)

SalesReturns(
    ReturnID,
    SaleID,
    ReturnDate,
    TotalRefund,
    Reason
)

PurchaseReturns(
    ReturnID,
    PurchaseID,
    ReturnDate,
    TotalRefund,
    Reason
)

AuditLog(
    LogID,
    EntityType,
    EntityID,
    Action,
    OldValue,
    NewValue,
    ChangedBy,
    ChangedDate
)
"""

_SYSTEM_PROMPT = f"""
You are an expert SQL generator for the InsightMart SQLite database.
Follow these rules EXACTLY:

1) Use ONLY the tables and columns listed in the schema below. Do NOT invent or rename any table/column.
2) Use SQLITE-compatible SQL (this is SQLite). Do NOT use MySQL/Postgres-specific functions (e.g., DATE_SUB, INTERVAL).
   Use date('now','-1 month'), date('now','-7 days'), strftime('%Y-%m', SaleDate) etc.
3) When a column may be NULL, prefer COALESCE(column, 'Unknown') or COALESCE(column, 0) so results are readable.
4) Return ONLY the SQL query text as the assistant response — no explanation, no commentary, no markdown fences.
5) If the user asks for "top N", generate LIMIT N; if N not provided, default to LIMIT 10 for "top" requests.
6) Use table aliases for readability (c, s, sd, p, etc.).
7) For time ranges, interpret "last month" as date('now','-1 month'), "last 30 days" as date('now','-30 days').
8) If the user requests results by city and some city values are NULL, use COALESCE(c.City,'Unknown') and group by that expression.
9) Prefer explicit GROUP BY and ORDER BY when aggregating; include sensible LIMIT where appropriate.
10) If a join might lose rows because a FK is missing, use LEFT JOIN and COALESCE to preserve totals unless the user explicitly requests otherwise.
11) Always use COALESCE(column, 0) — never prefix with table aliases.
12) Never join Customers table unless the user specifically asks for customer-level information.
13) Daily/weekly/monthly sales queries must use ONLY the Sales table and group by DATE(SaleDate).

Schema:
{_SCHEMA}
"""

def generate_sql_from_prompt(prompt: str) -> str:
    """
    Generate SQLite-compatible SQL using the Hugging Face chat API.
    Returns SQL string or an error string starting with "ERROR:".
    """

    hf_token = os.getenv("HUGGINGFACE_API_KEY")
    if not hf_token:
        return "ERROR: HuggingFace API key missing. Set HUGGINGFACE_API_KEY in Streamlit secrets."

    client = InferenceClient(token=hf_token)

    messages = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]

    try:
        resp = client.chat_completion(
            model=HF_MODEL_ID,
            messages=messages,
            max_tokens=300,
            temperature=0.2,
            top_p=0.95,
        )
        sql = resp["choices"][0]["message"]["content"].strip()

        # strip code fences if present
        if sql.startswith("```"):
            lines = sql.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            sql = "\n".join(lines).strip()

        return sql

    except Exception as e:
        return f"ERROR: Hugging Face call failed: {str(e)}"
