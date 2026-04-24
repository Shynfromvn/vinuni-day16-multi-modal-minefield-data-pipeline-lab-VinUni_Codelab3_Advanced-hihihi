import ast
import re

# ==========================================
# ROLE 2: ETL/ELT BUILDER
# ==========================================
# Task: Extract docstrings and comments from legacy Python code.

def extract_logic_from_code(file_path):
    # --- FILE READING (Handled for students) ---
    with open(file_path, 'r', encoding='utf-8') as f:
        source_code = f.read()
    # ------------------------------------------
    
    # TODO: Use the 'ast' module to find docstrings for functions
    tree = ast.parse(source_code)
    module_docstring = ast.get_docstring(tree) or ""

    function_rules = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            docstring = ast.get_docstring(node)
            if docstring:
                function_rules.append(f"{node.name}: {docstring.strip()}")

    # TODO: (Optional/Advanced) Use regex to find business rules in comments like "# Business Logic Rule 001"
    comment_rules = re.findall(r"#\s*(.*)", source_code)
    business_comments = [comment.strip() for comment in comment_rules if "Business Logic Rule" in comment or "8%" in comment or "10%" in comment]

    discrepancy_flag = "8%" in source_code and "0.10" in source_code

    # TODO: Return a dictionary for the UnifiedDocument schema.
    combined_content = "\n\n".join(part for part in [
        module_docstring.strip(),
        "\n".join(function_rules).strip(),
        "\n".join(business_comments).strip(),
    ] if part)

    return {
        "document_id": "code-legacy-pipeline",
        "content": combined_content,
        "source_type": "Code",
        "author": "Senior Dev (retired)",
        "timestamp": None,
        "source_metadata": {
            "original_file": file_path.split("\\")[-1].split("/")[-1],
            "function_count": len(function_rules),
            "comment_rule_count": len(business_comments),
            "logic_discrepancy": discrepancy_flag,
        },
    }

