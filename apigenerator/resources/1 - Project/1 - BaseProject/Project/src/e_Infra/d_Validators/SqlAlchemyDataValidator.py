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
_raw_date_masks = get_global_variable('date_valid_masks').split(',')
_CACHED_VALID_DATE_MASKS = [mask.strip() for mask in _raw_date_masks if mask.strip()]

_raw_time_masks = get_global_variable('time_valid_masks').split(',')
_CACHED_VALID_TIME_MASKS = [mask.strip() for mask in _raw_time_masks if mask.strip()]

_CACHED_VALID_DATETIME_MASKS = []
for _date_mask in _CACHED_VALID_DATE_MASKS:
    for _time_mask in _CACHED_VALID_TIME_MASKS:
        _CACHED_VALID_DATETIME_MASKS.append(f'{_date_mask} {_time_mask}')
        _CACHED_VALID_DATETIME_MASKS.append(f'{_date_mask}T{_time_mask}')

# --- Module-level Cache for Column Type Information ---
_COLUMN_TYPE_INFO_CACHE = {}
# --- End Caches ---


def validate_request_data_object(declarative_meta, request_data_object):
    try:
        validate_build(declarative_meta, request_data_object)
        validate_python_type(declarative_meta, request_data_object)
        declarative_meta.validate_custom_rules(request_data_object)
        if isinstance(request_data_object, dict):
             validate_datetime_masks(declarative_meta, request_data_object)
    except Exception as e:
        raise e


def get_valid_datetime_masks():
    return _CACHED_VALID_DATETIME_MASKS


def validate_datetime(column, request_data):
    valid_datetime_masks_to_check = get_valid_datetime_masks()
    for datetime_mask in valid_datetime_masks_to_check:
        try:
            request_data[column.key] = datetime.strptime(
                str(request_data.get(column.key)), datetime_mask)
            return
        except (ValueError, TypeError, AttributeError):
            continue
    raise Exception(f'Invalid datetime value for {column.name} attribute: {request_data.get(column.key)}')


def validate_date(column, request_data):
    for date_mask in _CACHED_VALID_DATE_MASKS:
        try:
            request_data[column.name] = datetime.strptime(
                str(request_data.get(column.name)), date_mask).date()
            return
        except (ValueError, TypeError, AttributeError):
            continue
    raise Exception(f'Invalid date value for {column.name} attribute: {request_data.get(column.name)}')


def validate_time(column, request_data):
    for time_mask in _CACHED_VALID_TIME_MASKS:
        try:
            request_data[column.name] = datetime.strptime(
                str(request_data.get(column.name)), time_mask).time()
            return
        except (ValueError, TypeError, AttributeError):
            continue
    raise Exception(f'Invalid time value for {column.name} attribute: {request_data.get(column.name)}')


def validate_year(column, year_dict):
    year_value_str = str(year_dict.get(column.name))
    try:
        if '-' not in year_value_str and '/' not in year_value_str and year_value_str.isdigit():
            if re.match(r"^\d{4}$", year_value_str):
                year_integer = int(year_value_str)
                if 1000 <= year_integer <= 9999:
                    return 'year'
    except Exception as e:
        raise Exception(f"Error processing year {year_value_str} for {column.name}: {e}")
    raise Exception(f'Invalid year value for {column.name} attribute: {year_value_str}')


def validate_year_month(column, data_dict):
    date_str = str(data_dict.get(column.name))
    original_date_str = date_str
    try:
        temp_day_to_append = "-01" if '-' in date_str else "/01"
        if '-' in date_str:
            parts = date_str.split('-')
            date_str_to_validate = f"{parts[0]}-{parts[1]}{temp_day_to_append}" if len(parts[0]) == 4 else f"{parts[1]}-{parts[0]}{temp_day_to_append}"
        elif '/' in date_str:
            parts = date_str.split('/')
            date_str_to_validate = f"{parts[0]}/{parts[1]}{temp_day_to_append}" if len(parts[0]) == 4 else f"{parts[1]}/{parts[0]}{temp_day_to_append}"
        else:
            raise ValueError("Invalid year-month format. Use YYYY-MM or YYYY/MM.")

        temp_data_for_validation = {column.name: date_str_to_validate}
        validate_date(column, temp_data_for_validation)
        return 'year-month'
    except Exception as e:
        raise Exception(f'Invalid year-month value for {column.name} attribute: {original_date_str}. Error: {e}')


def validate_all_datetime_types(column, start_and_end_strings):
    for date_str_value in start_and_end_strings:
        data_dict = {column.name: date_str_value}
        try:
            validate_datetime(column, data_dict.copy())
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
            if validate_year(column, data_dict.copy()) == 'year': return 'year'
        except Exception: pass
        try:
            if validate_year_month(column, data_dict.copy()) == 'year-month': return 'year-month'
        except Exception: pass
    raise Exception(f'Failed to validate {column.name} as any known date/time type for value: {start_and_end_strings[0]}')


def validate_non_serializable_types(query, declarative_meta):
    global _COLUMN_TYPE_INFO_CACHE
    declarative_meta_name = declarative_meta.__name__

    if declarative_meta_name not in _COLUMN_TYPE_INFO_CACHE:
        table_columns = inspect(declarative_meta).columns
        all_column_keys = [col.key for col in table_columns]
        set_type_column_keys = [col.key for col in table_columns if str(col.type) == 'SET']
        _COLUMN_TYPE_INFO_CACHE[declarative_meta_name] = (all_column_keys, set_type_column_keys)

    all_column_keys, set_type_column_keys = _COLUMN_TYPE_INFO_CACHE[declarative_meta_name]

    if not set_type_column_keys: # If no SET type columns, return query as is
        return query

    try:
        result = []
        for item in query: # Assuming query is iterable of ORM objects or similar
            item_dict = {}
            # First, populate item_dict with all column values
            for key in all_column_keys:
                item_dict[key] = getattr(item, key, None)

            # Then, process only the SET type columns for string conversion
            for set_key in set_type_column_keys:
                value = item_dict.get(set_key) # Value already fetched
                if value is not None: # Ensure value is not None before joining
                    item_dict[set_key] = ",".join(map(str, value))
            result.append(item_dict)
        return result
    except Exception as e:
        # It's good practice to log the actual error e here
        raise Exception(f'Failed to process non-serializable types for {declarative_meta_name}: {e}')


def validate_and_parse_interval(column, request_data):
    # Consider making interval_pattern a module-level constant if used frequently or complex
    interval_pattern = re.compile(r'(?P<number>\d+)\s*(?P<unit>days?)')
    value_to_parse = str(request_data.get(column.name))
    match = interval_pattern.match(value_to_parse)
    if match:
        number = int(match.group('number'))
        request_data[column.name] = timedelta(days=number)
        return
    raise ValueError(f"Cannot parse interval: {request_data.get(column.name)} for column {column.name}")


def validate_datetime_masks(declarative_meta, request_data_object: dict):
    if request.method == 'GET':
        return

    declarative_meta_columns = inspect(declarative_meta).columns
    columns_by_key = {col.key: col for col in declarative_meta_columns}

    for key, value in request_data_object.items():
        if value is None:
            continue

        declarative_meta_item = columns_by_key.get(key)
        if not declarative_meta_item:
            continue

        column_type_str = str(declarative_meta_item.type).lower()
        try:
            if column_type_str in ('timestamp', 'datetime'):
                is_timedelta_type = False
                try:
                    if hasattr(declarative_meta_item.type, 'python_type') and \
                       declarative_meta_item.type.python_type == timedelta:
                        is_timedelta_type = True
                except AttributeError:
                    pass
                if is_timedelta_type:
                    validate_and_parse_interval(declarative_meta_item, request_data_object)
                else:
                    validate_datetime(declarative_meta_item, request_data_object)
            elif column_type_str == 'date':
                validate_date(declarative_meta_item, request_data_object)
            elif column_type_str == 'time':
                validate_time(declarative_meta_item, request_data_object)
        except Exception as e:
            raise e


def get_declarative_meta_attribute_definitions(attribute_key, declarative_meta_attribute_list):
    for item in declarative_meta_attribute_list:
        if str(item.key) == str(attribute_key):
            return item
    return None


def validate_build(declarative_meta, request_data_object):
    try:
        build_domain_object_from_dict(declarative_meta, request_data_object)
    except Exception as e:
        table_name = getattr(declarative_meta, '__tablename__', declarative_meta.__name__)
        raise Exception(str(e).replace('__init__()', table_name))


def cast_types_that_match(request_value, domain_value_type):
    match_types = {"float": "int"}
    if domain_value_type.__name__ in match_types:
        expected_request_type_name = match_types[domain_value_type.__name__]
        if type(request_value).__name__ == expected_request_type_name:
            try:
                return domain_value_type(request_value)
            except (ValueError, TypeError):
                return None
    return None


def validate_python_type(declarative_meta, request_data_object):
    if not hasattr(declarative_meta, '__annotations__'):
        return

    annotations = declarative_meta.__annotations__
    for key, value in request_data_object.items():
        if key in annotations:
            expected_type = annotations[key]
            if not isinstance(value, expected_type):
                casted_value = cast_types_that_match(value, expected_type)
                if casted_value is not None and isinstance(casted_value, expected_type):
                    request_data_object[key] = casted_value
                else:
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
        declarative_meta_attr = [str(key) for key in getattr(declarative_meta.schema, 'dump_fields', {}).keys()]
        if not declarative_meta_attr and hasattr(declarative_meta, '__table__'):
             declarative_meta_attr = [col.key for col in inspect(declarative_meta).columns]
        for key_select in header_args.get('HTTP_SELECT'):
            if key_select != '' and key_select not in declarative_meta_attr:
                table_name = getattr(declarative_meta, '__tablename__', declarative_meta.__name__)
                raise Exception(
                    f"{table_name} select got an unexpected keyword argument '{key_select}'"
                )


def validate_order_by(declarative_meta, header_args):
    http_orderby = header_args.get('HTTP_ORDERBY')
    if http_orderby and http_orderby[0] != '':
        declarative_meta_attr = [str(key) for key in getattr(declarative_meta.schema, 'dump_fields', {}).keys()]
        if not declarative_meta_attr and hasattr(declarative_meta, '__table__'):
             declarative_meta_attr = [col.key for col in inspect(declarative_meta).columns]
        if http_orderby[0] not in declarative_meta_attr:
            raise Exception(
                f"orderby got an unexpected keyword argument '{http_orderby[0]}'"
            )
        if len(http_orderby) == 2:
            if http_orderby[1].lower() not in ['asc', 'desc']:
                raise Exception(
                    f"'{http_orderby[1]}' not a valid argument for orderby direction. Must be either 'asc' or 'desc'"
                )
        elif len(http_orderby) > 2:
             raise Exception("orderby has too many arguments. Expected field name and optional direction ('asc'/'desc').")


def validate_group_by(declarative_meta, header_args):
    http_groupby = header_args.get('HTTP_GROUPBY')
    if http_groupby and http_groupby[0] != '':
        declarative_meta_attr = [str(key) for key in getattr(declarative_meta.schema, 'dump_fields', {}).keys()]
        if not declarative_meta_attr and hasattr(declarative_meta, '__table__'):
             declarative_meta_attr = [col.key for col in inspect(declarative_meta).columns]
        for header_item in http_groupby:
            if header_item not in declarative_meta_attr:
                raise Exception(
                    f"groupby got an unexpected keyword argument '{header_item}'"
                )
