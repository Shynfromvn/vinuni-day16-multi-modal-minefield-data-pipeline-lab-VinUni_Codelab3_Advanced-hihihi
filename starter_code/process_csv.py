import pandas as pd


def _normalize_price(value):
    if pd.isna(value):
        return None

    text = str(value).strip()
    if not text or text.upper() in {"N/A", "NULL"} or text.lower() == "liên hệ":
        return None
    if text.lower() == "five dollars":
        return 5.0

    cleaned = text.replace("$", "").replace(",", "").replace("VND", "").replace("USD", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return None


def _normalize_date(value):
    if pd.isna(value):
        return None

    text = str(value).strip()
    if not text:
        return None

    date_formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%Y/%m/%d",
        "%d %b %Y",
        "%B %dth %Y",
        "%B %dst %Y",
        "%B %dnd %Y",
        "%B %drd %Y",
    ]
    for fmt in date_formats:
        parsed = pd.to_datetime(text, format=fmt, errors="coerce")
        if pd.notna(parsed):
            return parsed.strftime("%Y-%m-%d")
    return None

# ==========================================
# ROLE 2: ETL/ELT BUILDER
# ==========================================
# Task: Process sales records, handling type traps and duplicates.

def process_sales_csv(file_path):
    # --- FILE READING (Handled for students) ---
    df = pd.read_csv(file_path)
    # ------------------------------------------
    
    # TODO: Remove duplicate rows based on 'id'
    df = df.drop_duplicates(subset=["id"], keep="first").copy()

    # TODO: Clean 'price' column: convert "$1200", "250000", "five dollars" to floats
    df["normalized_price"] = df["price"].apply(_normalize_price)

    # TODO: Normalize 'date_of_sale' into a single format (YYYY-MM-DD)
    df["normalized_date"] = df["date_of_sale"].apply(_normalize_date)

    # TODO: Return a list of dictionaries for the UnifiedDocument schema.
    documents = []
    for row in df.to_dict(orient="records"):
        stock_quantity = row.get("stock_quantity")
        if pd.isna(stock_quantity):
            stock_quantity = None
        else:
            stock_quantity = int(float(stock_quantity))

        doc = {
            "document_id": f"csv-{row['id']}",
            "content": (
                f"Product {row['product_name']} in category {row['category']} "
                f"was sold on {row['normalized_date'] or 'unknown-date'} "
                f"for {row['normalized_price']} {row['currency']}."
            ),
            "source_type": "CSV",
            "author": str(row.get("seller_id", "Unknown")),
            "timestamp": row["normalized_date"] if pd.notna(row["normalized_date"]) else None,
            "source_metadata": {
                "product_name": row["product_name"],
                "category": row["category"],
                "normalized_price": row["normalized_price"],
                "currency": row["currency"],
                "seller_id": row.get("seller_id"),
                "stock_quantity": stock_quantity,
                "raw_price": row.get("price"),
            },
        }
        documents.append(doc)

    return documents

