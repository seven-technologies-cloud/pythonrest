# Method resolves which filter will be applied to a string class attribute by default or custom definitions #
def resolve_string_filter(declarative_meta, class_object, class_object_attr, query, equals_type_str):
    # Get the SQLAlchemy column object and the filter value once
    column_to_filter = getattr(declarative_meta, class_object_attr)
    filter_value = getattr(class_object, class_object_attr)

    # Use if/elif structure for clarity and efficiency
    if equals_type_str == 'left_like':
        # Returning filter for left-sided like strings (e.g., value LIKE '%filter_value')
        return query.filter(column_to_filter.like(f'%{filter_value}'))
    elif equals_type_str == 'right_like':
        # Returning filter for right-sided like strings (e.g., value LIKE 'filter_value%')
        return query.filter(column_to_filter.like(f'{filter_value}%'))
    elif equals_type_str == 'full_like':
        # Returning filter for both-sided like strings (e.g., value LIKE '%filter_value%')
        return query.filter(column_to_filter.like(f'%{filter_value}%'))
    elif equals_type_str == 'regular':
        # Returning filter for exact match
        return query.filter(column_to_filter == filter_value)
    else:
        # If equals_type_str is not recognized, return the query unmodified.
        # Consider logging a warning or raising an error for unknown types if stricter handling is needed.
        return query