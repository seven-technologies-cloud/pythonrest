def adding_replace_in_column_name_with_spaces(column_name: str) -> str:
    separators = ["-", "_", " ", ".", "/", "\\", ":", "~", "*", "+", "|", "@"]

    for separator in separators:
        if separator in column_name:
            column_name = column_name.replace(separator, '_')
            return column_name

    return column_name
