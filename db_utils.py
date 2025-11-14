import re

def is_safe_sql(sql: str) -> bool:
    sql_clean = sql.strip().lower()

    forbidden = [
        r"\bupdate\b",
        r"\bdelete\b",
        r"\binsert\b",
        r"\bdrop\b",
        r"\btruncate\b",
        r"\balter\b",
        r"\bcreate\b",
        r"\breplace\b",
        r"\battach\b",
        r"\bdetach\b",
        r"\bpragma\b"
    ]

    for pattern in forbidden:
        if re.search(pattern, sql_clean):
            return False

    # Allowed commands: SELECT or WITH only
    if sql_clean.startswith("select") or sql_clean.startswith("with"):
        return True

    return False
