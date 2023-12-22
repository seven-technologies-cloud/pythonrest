# Method returns a system message according to given parameter #
def get_system_message(message_key):
    system_messages = {
        'message': 'Message',
        'error_message': 'ErrorMessage',
        'error_list': 'ErrorList',
        'empty_json': 'JSON body empty',
        'invalid_sql_injection': 'SQL query blocked, possible injection attributes',
        'invalid_sql_method': 'SQL query blocked, invalid SQL verb for HTTP method',
        'invalid_sql': 'Invalid SQL query',
        'where_is_required': 'Missing WHERE clause',
        'invalid_syntax': 'Invalid syntax for SQL query',
        'table_does_not_exist': 'Table does not exist',
        'query_success': 'Query successfully persisted',
        'get_no_items_found': 'No items found.',
        'delete_no_items_found': 'No match found to delete',
        'patch_no_items_found': 'No match to update',
        'object_set_persisted_success': 'Object(s) successfully persisted.',
        'object_deleted_success': 'Object successfully deleted.',
        'malformed_input_data': 'Malformed input data',
        'malformed_header_params': 'Malformed header parameters',
        'dict_from_body_no_pk_patch': 'Primary key missing',
        'id_not_found': 'Parameter id not found.',
        'foreign_key_mandatory': 'Foreign key is mandatory.',
        'cannot_update_with_id_only': 'Cannot update with id only.',
        'invalid_connection_parameters': "Invalid database connection parameters"
    }

    return system_messages.get(message_key, 'Unknown message')
