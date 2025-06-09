# Builder Imports #
from src.e_Infra.b_Builders.DomainObjectBuilder import build_domain_object_from_dict

# Infra Imports #
from src.e_Infra.GlobalVariablesManager import *

# SqlAlchemy Imports #
from sqlalchemy.inspection import inspect

# System Imports #
from datetime import datetime, timedelta, date
import re

# Flask Imports #
from flask import request

# --- Module-level Caches for Date/Time Masks ---
# Assuming get_global_variable can be called at module load time.
_raw_date_masks = get_global_variable('date_valid_masks').split(',')
_CACHED_VALID_DATE_MASKS = [mask.strip() for mask in _raw_date_masks if mask.strip()]

_raw_time_masks = get_global_variable('time_valid_masks').split(',')
_CACHED_VALID_TIME_MASKS = [mask.strip() for mask in _raw_time_masks if mask.strip()]

_CACHED_VALID_DATETIME_MASKS = []
for _date_mask in _CACHED_VALID_DATE_MASKS:
    for _time_mask in _CACHED_VALID_TIME_MASKS:
        _CACHED_VALID_DATETIME_MASKS.append(f'{_date_mask} {_time_mask}')
        _CACHED_VALID_DATETIME_MASKS.append(f'{_date_mask}T{_time_mask}')
# --- End Caches ---


def validate_request_data_object(declarative_meta, request_data_object):
    try:
        # Validate Builder attributes
        validate_build(declarative_meta, request_data_object)

        # Validate Python types for attributes
        validate_python_type(declarative_meta, request_data_object)

        # Custom validators
        declarative_meta.validate_custom_rules(request_data_object)

        # Apply valid date/datetime/timestamp masks
        # Ensure request_data_object is a dictionary before passing
        if isinstance(request_data_object, dict):
             validate_datetime_masks(declarative_meta, request_data_object)
        # If request_data_object is a list of dicts (e.g. from a batch request),
        # this validation might need to be called for each dict in the list by the caller.
        # Current structure of validate_datetime_masks expects a single dict.

    except Exception as e:
        raise e


def get_valid_datetime_masks():
    """Returns the cached list of combined datetime masks."""
    return _CACHED_VALID_DATETIME_MASKS


def validate_datetime(column, request_data):
    # Uses _CACHED_VALID_DATETIME_MASKS (implicitly via get_valid_datetime_masks)
    # The original called get_valid_datetime_masks() inside, which is now optimized.
    # No change needed here other than relying on the cached version from get_valid_datetime_masks.
    valid_datetime_masks_to_check = get_valid_datetime_masks()
    for datetime_mask in valid_datetime_masks_to_check: # Changed variable name for clarity
        try:
            # request_data.get(column.key) is safer if key might be missing, but current code uses direct access.
            # Sticking to direct access as per original, assuming key exists.
            request_data[column.key] = datetime.strptime(
                str(request_data.get(column.key)), datetime_mask) # Ensure value is string
            return
        except (ValueError, TypeError, AttributeError): # Catch more specific errors
            continue
    raise Exception(f'Invalid datetime value for {column.name} attribute: {request_data.get(column.key)}')


def validate_date(column, request_data):
    # Uses _CACHED_VALID_DATE_MASKS
    for date_mask in _CACHED_VALID_DATE_MASKS:
        try:
            request_data[column.name] = datetime.strptime(
                str(request_data.get(column.name)), date_mask).date() # Ensure value is string, convert to date
            return
        except (ValueError, TypeError, AttributeError):
            continue
    raise Exception(f'Invalid date value for {column.name} attribute: {request_data.get(column.name)}')


def validate_time(column, request_data):
    # Uses _CACHED_VALID_TIME_MASKS
    for time_mask in _CACHED_VALID_TIME_MASKS:
        try:
            request_data[column.name] = datetime.strptime(
                str(request_data.get(column.name)), time_mask).time() # Ensure value is string, convert to time
            return
        except (ValueError, TypeError, AttributeError):
            continue
    raise Exception(f'Invalid time value for {column.name} attribute: {request_data.get(column.name)}')


def validate_year(column, year_dict): # Expects a dict like {column.name: year_value_str}
    year_value_str = str(year_dict.get(column.name)) # Ensure string
    try:
        if '-' not in year_value_str and '/' not in year_value_str and year_value_str.isdigit():
            if re.match(r"^\d{4}$", year_value_str):
                year_integer = int(year_value_str)
                # Basic check for a reasonable year range if needed, e.g., 1000-9999
                if 1000 <= year_integer <= 9999:
                    # To store just the year as an int, or as a date object:
                    # year_dict[column.name] = year_integer # Or date(year_integer, 1, 1) if type consistency is needed
                    return 'year' # Indicate 'year' type was validated
    except Exception as e: # Broad exception for safety, could be more specific
        raise Exception(f"Error processing year {year_value_str} for {column.name}: {e}")
    raise Exception(f'Invalid year value for {column.name} attribute: {year_value_str}')


def validate_year_month(column, data_dict): # Expects {column.name: date_str}
    date_str = str(data_dict.get(column.name)) # Ensure string
    original_date_str = date_str # For error messages
    try:
        temp_day_to_append = "-01" if '-' in date_str else "/01"
        if '-' in date_str:
            parts = date_str.split('-')
            if len(parts[0]) == 4: # YYYY-MM
                date_str_to_validate = f"{parts[0]}-{parts[1]}{temp_day_to_append}"
            else: # MM-YYYY
                date_str_to_validate = f"{parts[1]}-{parts[0]}{temp_day_to_append}" # Reorder for consistent parsing if needed
                # Or decide on a specific format like YYYY-MM and parse parts[1] as year, parts[0] as month
                # For simplicity, assuming the validate_date handles various full date masks.
                # This part might need more robust parsing depending on allowed year-month input formats.
        elif '/' in date_str:
            parts = date_str.split('/')
            if len(parts[0]) == 4: # YYYY/MM
                date_str_to_validate = f"{parts[0]}/{parts[1]}{temp_day_to_append}"
            else: # MM/YYYY
                date_str_to_validate = f"{parts[1]}/{parts[0]}{temp_day_to_append}"
        else:
            raise ValueError("Invalid year-month format. Use YYYY-MM or YYYY/MM.")

        # Validate as a full date (e.g., YYYY-MM-01)
        # Create a temporary dict for validate_date as it expects dict access
        temp_data_for_validation = {column.name: date_str_to_validate}
        validate_date(column, temp_data_for_validation) # This will parse and store if valid
        # If successful, store the validated date object (or a year-month specific representation if desired)
        # request_data[column.name] = temp_data_for_validation[column.name] # Example if storing as full date object
        return 'year-month' # Indicate 'year-month' type was validated

    except Exception as e: # Catch errors from parsing or validation
        raise Exception(f'Invalid year-month value for {column.name} attribute: {original_date_str}. Error: {e}')


def validate_all_datetime_types(column, start_and_end_strings): # start_and_end_strings is actually a list of date strings
    # This function attempts to identify the type of a list of date strings
    # by trying different validation functions. It returns a string like 'datetime', 'date', 'time'.
    # It does NOT modify request_data_object. It's a type checker.
    # The modification of request_data_object happens in validate_datetime_masks.
    for date_str_value in start_and_end_strings:
        data_dict = {column.name: date_str_value} # Create dict for validation functions
        try:
            validate_datetime(column, data_dict.copy()) # Use .copy() if validator modifies dict and we don't want it here
            return 'datetime'
        except Exception: pass
        try:
            validate_date(column, data_dict.copy())
            return 'date'
        except Exception: pass
        try:
            validate_time(column, data_dict.copy())
            return 'time'
        except Exception: pass
        try:
            # validate_year expects dict {column.name: value}
            if validate_year(column, data_dict.copy()) == 'year': return 'year'
        except Exception: pass
        try:
            # validate_year_month expects dict {column.name: value}
            if validate_year_month(column, data_dict.copy()) == 'year-month': return 'year-month'
        except Exception: pass
    raise Exception(f'Failed to validate {column.name} as any known date/time type for value: {start_and_end_strings[0]}')


def validate_non_serializable_types(query, declarative_meta):
    try:
        result = []
        column_attributes = [getattr(declarative_meta, col.key)
                             for col in declarative_meta.__table__.columns]
        has_set_type = any(f'{field.type}' == 'SET' for field in column_attributes) # Simplified any()
        if has_set_type:
            for item in query: # Assuming query is iterable of ORM objects or similar
                item_dict = {}
                for field_col_obj in column_attributes: # Use a more descriptive name
                    value = getattr(item, field_col_obj.key, None)
                    item_dict[field_col_obj.key] = value
                    if value is not None and str(field_col_obj.type) == 'SET': # More robust type check
                        item_dict[field_col_obj.key] = ",".join(map(str, value))
                result.append(item_dict)
            return result
        return query # Return original query if no SET types
    except Exception as e:
        raise Exception(f'Failed to validate non serializable types:  {e}')


def validate_and_parse_interval(column, request_data):
    interval_pattern = re.compile(r'(?P<number>\d+)\s*(?P<unit>days?)') # This could be module level
    value_to_parse = str(request_data.get(column.name)) # Ensure string
    match = interval_pattern.match(value_to_parse)
    if match:
        number = int(match.group('number'))
        # unit = match.group('unit') # unit is not strictly needed if only days are supported
        request_data[column.name] = timedelta(days=number)
        return
    raise ValueError(f"Cannot parse interval: {request_data.get(column.name)} for column {column.name}")


def validate_datetime_masks(declarative_meta, request_data_object: dict): # Explicitly type hint as dict
    if request.method == 'GET': # Skip for GET requests as per original logic
        return

    # Optimized column definition lookup
    declarative_meta_columns = inspect(declarative_meta).columns
    columns_by_key = {col.key: col for col in declarative_meta_columns}

    for key, value in request_data_object.items(): # Iterate key-value pairs
        if value is None: # Skip None values, they don't need mask validation
            continue

        declarative_meta_item = columns_by_key.get(key)
        if not declarative_meta_item:
            continue # Key from request_data_object is not a defined column

        # Ensure value is a string before attempting string-based type checks
        # However, type validation should ideally happen before mask validation.
        # Assuming value is string here as per context of mask application.
        # If not, str(value) would be needed in validator functions.

        column_type_str = str(declarative_meta_item.type).lower()

        try:
            if column_type_str in ('timestamp', 'datetime'):
                # Check for timedelta/interval type if column's python_type is timedelta
                is_timedelta_type = False
                try:
                    # Accessing python_type can be tricky; some custom types might not have it directly.
                    # A more robust check might involve inspecting declarative_meta_item.type itself.
                    if hasattr(declarative_meta_item.type, 'python_type') and \
                       declarative_meta_item.type.python_type == timedelta:
                        is_timedelta_type = True
                except AttributeError: # some types might not have python_type
                    pass

                if is_timedelta_type: # Example check, might need refinement
                    validate_and_parse_interval(declarative_meta_item, request_data_object)
                else:
                    validate_datetime(declarative_meta_item, request_data_object)
            elif column_type_str == 'date':
                validate_date(declarative_meta_item, request_data_object)
            elif column_type_str == 'time':
                validate_time(declarative_meta_item, request_data_object)
            # Add year and year-month if they are distinct types to be validated here too.
            # Current logic in validate_all_datetime_types seems to handle them, but not directly called here.
            # This function is about applying the *final* transformation based on type.
        except Exception as e: # Catch validation error and enrich it
            # This makes errors from validate_datetime, validate_date, validate_time more informative
            # by including which validator failed, if not already clear from their messages.
            # However, those functions already raise specific messages.
            # Re-raising here might be redundant unless adding more context.
            # For now, let them propagate.
            raise e


def get_declarative_meta_attribute_definitions(attribute_key, declarative_meta_attribute_list):
    # This function is no longer used by validate_datetime_masks after optimization.
    # It might be used elsewhere or can be deprecated if not.
    for item in declarative_meta_attribute_list:
        if str(item.key) == str(attribute_key):
            return item
    return None # Explicitly return None if not found


def validate_build(declarative_meta, request_data_object):
    try:
        # build_domain_object_from_dict might not expect a list of dicts.
        # If request_data_object can be a list here, this needs a loop.
        # Assuming it's a single dict for now as per its usage in validate_request_data_object.
        build_domain_object_from_dict(declarative_meta, request_data_object)
    except Exception as e:
        # Modify the error message to be more specific about the table/entity
        table_name = getattr(declarative_meta, '__tablename__', declarative_meta.__name__)
        raise Exception(str(e).replace('__init__()', table_name))


def cast_types_that_match(request_value, domain_value_type):
    # This function attempts to cast between a few specific types (float to int).
    # It's quite limited. A more general approach or using a library might be better if more casts are needed.
    match_types = {"float": "int"} # This means if domain is float, and request is int, cast request to float.
    # The current logic is: if domain_value_type is float, and type(request_value) is int, then cast.
    if domain_value_type.__name__ in match_types: # e.g. domain_value_type is float
        expected_request_type_name = match_types[domain_value_type.__name__] # e.g. expected_request_type_name is "int"
        if type(request_value).__name__ == expected_request_type_name: # if type(request_value) is int
            try:
                return domain_value_type(request_value) # return float(request_value)
            except (ValueError, TypeError): # Handle potential errors during casting
                return None
    return None


def validate_python_type(declarative_meta, request_data_object):
    # Assuming request_data_object is a dictionary
    if not hasattr(declarative_meta, '__annotations__'):
        return # No annotations to validate against

    annotations = declarative_meta.__annotations__
    for key, value in request_data_object.items(): # Iterate items for both key and value
        if key in annotations:
            expected_type = annotations[key]
            if not isinstance(value, expected_type): # Use isinstance for type checking
                casted_value = cast_types_that_match(value, expected_type)
                if casted_value is not None and isinstance(casted_value, expected_type):
                    request_data_object[key] = casted_value
                else:
                    # More robust error for type mismatch
                    type_value_str = str(type(value)).replace("<class '", "").replace("'>", "")
                    type_expected_str = str(expected_type).replace("<class '", "").replace("'>", "")
                    raise Exception(
                        f"Expected type '{type_expected_str}' for attribute '{key}' "
                        f"but received value '{value}' of type '{type_value_str}'"
                    )


def validate_header_args(declarative_meta, header_args):
    validate_select_args(declarative_meta, header_args)
    validate_order_by(declarative_meta, header_args)
    validate_group_by(declarative_meta, header_args)


def validate_select_args(declarative_meta, header_args):
    if header_args.get('HTTP_SELECT') is not None:
        # Use .keys() for marshmallow schema fields if that's what dump_fields is
        declarative_meta_attr = [str(key) for key in getattr(declarative_meta.schema, 'dump_fields', {}).keys()]
        if not declarative_meta_attr and hasattr(declarative_meta, '__table__'): # Fallback to table columns if no schema fields
             declarative_meta_attr = [col.key for col in inspect(declarative_meta).columns]

        for key_select in header_args.get('HTTP_SELECT'): # Renamed key to key_select
            if key_select != '' and key_select not in declarative_meta_attr:
                table_name = getattr(declarative_meta, '__tablename__', declarative_meta.__name__)
                raise Exception(
                    f"{table_name} select got an unexpected keyword argument '{key_select}'"
                )


def validate_order_by(declarative_meta, header_args):
    http_orderby = header_args.get('HTTP_ORDERBY')
    if http_orderby and http_orderby[0] != '': # Check if list exists and first element is not empty
        # Similar field source as validate_select_args
        declarative_meta_attr = [str(key) for key in getattr(declarative_meta.schema, 'dump_fields', {}).keys()]
        if not declarative_meta_attr and hasattr(declarative_meta, '__table__'):
             declarative_meta_attr = [col.key for col in inspect(declarative_meta).columns]

        if http_orderby[0] not in declarative_meta_attr:
            raise Exception(
                f"orderby got an unexpected keyword argument '{http_orderby[0]}'"
            )
        if len(http_orderby) == 2:
            if http_orderby[1].lower() not in ['asc', 'desc']: # Use lower() for case-insensitivity
                raise Exception(
                    f"'{http_orderby[1]}' not a valid argument for orderby direction. Must be either 'asc' or 'desc'"
                )
        elif len(http_orderby) > 2:
             raise Exception("orderby has too many arguments. Expected field name and optional direction ('asc'/'desc').")


def validate_group_by(declarative_meta, header_args):
    http_groupby = header_args.get('HTTP_GROUPBY')
    if http_groupby and http_groupby[0] != '':
        # Similar field source as validate_select_args
        declarative_meta_attr = [str(key) for key in getattr(declarative_meta.schema, 'dump_fields', {}).keys()]
        if not declarative_meta_attr and hasattr(declarative_meta, '__table__'):
             declarative_meta_attr = [col.key for col in inspect(declarative_meta).columns]

        for header_item in http_groupby: # Renamed header to header_item
            if header_item not in declarative_meta_attr:
                raise Exception(
                    f"groupby got an unexpected keyword argument '{header_item}'"
                )
# Several minor improvements and safety checks added throughout during refactoring:
# - Ensured values are strings before strptime.
# - Converted parsed dates/times to .date() or .time() objects.
# - Made error messages slightly more specific.
# - Used .get(key) for dict access in some places for safety, though original often used direct access.
# - Simplified some boolean conditions or list checks.
# - Added explicit type hint for request_data_object in validate_datetime_masks.
# - Renamed loop variables for clarity in some places.
# - Used str(type) consistently for string representation of types in error messages.
# - Added .lower() to 'asc'/'desc' check in validate_order_by.
# - The interval pattern in validate_and_parse_interval could also be a module-level constant.
# - validate_all_datetime_types now uses .copy() when passing data_dict to validators to prevent unintended side-effects if those validators modify the dict and it's not desired at that stage.
# - validate_year and validate_year_month now expect a dict like {column.name: value_str} for consistency with other validators.
# - validate_datetime_masks loop now iterates `request_data_object.items()` to get both key and value.
# - Added check for `value is None` in `validate_datetime_masks` to skip mask validation for nulls.
