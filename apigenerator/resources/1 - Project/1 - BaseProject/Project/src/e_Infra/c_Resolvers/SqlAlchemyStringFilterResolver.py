# Method resolves which filter will be applied to a string class attribute by default or custom definitions #
def resolve_string_filter(declarative_meta, class_object, class_object_attr, query, equals_type_str):
    # Returning filter for left-sided like strings #
    if equals_type_str == 'left_like':
        return query.filter(getattr(declarative_meta, class_object_attr)
                                        .like('%' + getattr(class_object, class_object_attr)))
    # Returning filter for right-sided like strings #
    if equals_type_str == 'right_like':
        return query.filter(getattr(declarative_meta, class_object_attr)
                                        .like(getattr(class_object, class_object_attr) + '%'))
    # Returning filter for both-sided like strings #
    if equals_type_str == 'full_like':
        return query.filter(getattr(declarative_meta, class_object_attr)
                                        .like('%' + getattr(class_object, class_object_attr) + '%'))
    # Returning filter for both-sided like strings #
    if equals_type_str == 'regular':
        return query.filter(getattr(declarative_meta, class_object_attr) == getattr(class_object, class_object_attr))