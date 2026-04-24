from bs4 import BeautifulSoup


def _parse_price_to_vnd(price_text):
    value = price_text.strip()
    if value in {"N/A", "Liên hệ"}:
        return None
    digits = value.replace("VND", "").replace(",", "").strip()
    return int(digits) if digits.isdigit() else None

# ==========================================
# ROLE 2: ETL/ELT BUILDER
# ==========================================
# Task: Extract product data from the HTML table, ignoring boilerplate.

def parse_html_catalog(file_path):
    # --- FILE READING (Handled for students) ---
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
    # ------------------------------------------
    
    # TODO: Use BeautifulSoup to find the table with id 'main-catalog'
    # TODO: Extract rows, handling 'N/A' or 'Liên hệ' in the price column.
    # TODO: Return a list of dictionaries for the UnifiedDocument schema.
    table = soup.find("table", id="main-catalog")
    if table is None:
        return []

    documents = []
    for row in table.select("tbody tr"):
        cells = [cell.get_text(" ", strip=True) for cell in row.find_all("td")]
        if len(cells) != 6:
            continue

        product_id, product_name, category, price_text, stock_text, rating_text = cells
        stock_value = int(stock_text) if stock_text.lstrip("-").isdigit() else None
        doc = {
            "document_id": f"html-{product_id}",
            "content": (
                f"Catalog item {product_name} belongs to {category} with listed price "
                f"{price_text} and stock level {stock_text}."
            ),
            "source_type": "HTML",
            "author": "VinShop",
            "timestamp": None,
            "source_metadata": {
                "product_code": product_id,
                "product_name": product_name,
                "category": category,
                "listed_price_text": price_text,
                "listed_price_vnd": _parse_price_to_vnd(price_text),
                "stock_quantity": stock_value,
                "rating": rating_text,
            },
        }
        documents.append(doc)

    return documents

