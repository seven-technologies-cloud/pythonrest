def adding_replace_in_column_name_with_spaces(column_name: str) -> str:
    separators = ["-", " ", ".", "/", "\\", ":", "~", "*", "+", "|", "@"]

    for separator in separators:
        if separator in column_name:
            column_name = column_name.replace(separator, '_')
            return column_name
    column_name = adding_replace_in_column_name_with_python_keys(column_name)
    return column_name

def adding_replace_in_column_name_with_python_keys(column_name: str) -> str:
    python_keywords = [
        "False", "None", "True", "and", "as", "assert", "async", "await",
        "break", "class", "continue", "def", "del", "elif", "else", "except",
        "finally", "for", "from", "global", "if", "import", "in", "is",
        "lambda", "nonlocal", "not", "or", "pass", "raise", "return", "try",
        "while", "with", "yield", "metadata"
    ]

    for keyword in python_keywords:
        if keyword == column_name:
            column_name = column_name.replace(keyword, keyword + '_prcolkey')
            return column_name
    return column_name