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


def validate_request_data_object(declarative_meta, request_data_object):
    try:
        # Validate Builder attributes
        validate_build(declarative_meta, request_data_object)

        # Validate Python types for attributes
        validate_python_type(declarative_meta, request_data_object)

        # Custom validators
        declarative_meta.validate_custom_rules(request_data_object)

        # Apply valid date/datetime/timestamp masks
        validate_datetime_masks(declarative_meta, request_data_object)

    except Exception as e:
        raise e


def get_valid_datetime_masks():
    valid_datetime_masks = list()
    valid_date_masks = get_global_variable('date_valid_masks').split(',')
    valid_time_masks = get_global_variable('time_valid_masks').split(',')
    for i in range(len(valid_date_masks)):
        for j in range(len(valid_time_masks)):
            valid_datetime_masks.append(
                f'{valid_date_masks[i].strip()} {valid_time_masks[j].strip()}')
            valid_datetime_masks.append(
                f'{valid_date_masks[i].strip()}T{valid_time_masks[j].strip()}')
    return valid_datetime_masks


def validate_datetime(column, request_data):
    valid_datetime_masks = get_valid_datetime_masks()
    for datetime_mask in valid_datetime_masks:
        try:
            request_data[column.key] = datetime.strptime(
                request_data.get(column.key), datetime_mask.strip())
            return
        except Exception as e:
            del e
            continue
    raise Exception(f'Invalid datetime value for {column.name} attribute')



def validate_date(column, request_data):
    valid_date_masks = get_global_variable('date_valid_masks').split(',')
    for date_mask in valid_date_masks:
        try:
            request_data[column.name] = datetime.strptime(
                request_data.get(column.name), date_mask.strip())
            return
        except Exception as e:
            del e
            continue
    raise Exception(f'Invalid date value for {column.name} attribute')


def validate_time(column, request_data):
    valid_time_masks = get_global_variable('time_valid_masks').split(',')
    for time_mask in valid_time_masks:
        try:
            request_data[column.name] = datetime.strptime(
                request_data.get(column.name), time_mask.strip())
            return
        except Exception as e:
            del e
            continue
    raise Exception(f'Invalid time value for {column.name} attribute')


def validate_year(column, year):
    year_value = year[column.name]
    try:
        if '-' not in year_value and '/' not in year_value and year_value.isdigit():
            if re.match(r"^\d{4}$", year_value):
                year_integer = int(year_value)
                date_obj = date(year_integer, 1, 1)

                if date_obj.year == year_integer:
                    return 'year'
    except Exception as e:
        raise Exception(f"Error processing year {year_value}: {e}")

    # If we reach here, it means no valid year was found
    raise Exception(f'Invalid year value for {column.name} attribute')


def validate_year_month(column, start_and_end_strings):
    for key, date_str in start_and_end_strings.items():
        try:
            if '-' in date_str:
                year_month = date_str.split('-')
                if len(year_month[0]) == 4:
                    date_str = f'{date_str}-01'
                    validate_date(column, {column.name: date_str})
                else:
                    date_str = f'01-{date_str}'
                    validate_date(column, {column.name: date_str})
            elif '/' in date_str:
                year_month = date_str.split('/')
                if len(year_month[0]) == 4:
                    date_str = f'{date_str}/01'
                    validate_date(column, {column.name: date_str})
                else:
                    date_str = f'01/{date_str}'
                    validate_date(column, {column.name: date_str})
            else:
                raise Exception(
                    f'Invalid year-month value for {column.name} attribute')
        except Exception as e:
            print(f"Error processing year and month {date_str}: {e}")
            continue
        else:
            # If all validations pass, return here
            return

    # If we reach here, it means no valid year was found
    raise Exception(f'Invalid year-month value for {column.name} attribute')


def validate_all_datetime_types(column, start_and_end_strings):
    for data in start_and_end_strings:
        data = {column.name: data}
        try:
            validate_datetime(column, data)
            return 'datetime'
        except Exception:
            pass

        try:
            validate_date(column, data)
            return 'date'
        except Exception:
            pass

        try:
            validate_time(column, data)
            return 'time'
        except Exception:
            pass

        try:
            year = validate_year(column, data)
            return year
        except Exception:
            pass

        try:
            validate_year_month(column, data)
            return 'year-month'
        except Exception:
            pass
    raise Exception(
        f'Failed to validate {column.name} as datetime, date, or time')


def validate_non_serializable_types(query, declarative_meta):
    try:
        result = []
        column_attributes = [getattr(declarative_meta, col.key)
                             for col in declarative_meta.__table__.columns]
        has_set_type = any(f'{field.type}' ==
                           'SET' for field in column_attributes)
        if has_set_type:
            for item in query:
                item_dict = {}
                for field in column_attributes:
                    value = getattr(item, field.key, None)
                    item_dict[field.key] = value
                    if value is not None and f'{field.type}' == 'SET':
                        set_to_string = ",".join(map(str, value))
                        item_dict[field.key] = set_to_string
                result.append(item_dict)
            return result
        return query
    except Exception as e:
        raise Exception(
            f'Failed to validate non serializable types:  {e}')


def validate_and_parse_interval(column, request_data):
    # This function will convert a string like "2 days" into a timedelta object.
    interval_pattern = re.compile(r'(?P<number>\d+)\s*(?P<unit>days?)')
    match = interval_pattern.match(request_data.get(column.name))
    if match:
        number = int(match.group('number'))
        unit = match.group('unit')

        if 'day' in unit:
            request_data[column.name] = timedelta(days=number)
            return
    raise ValueError(f"Cannot parse interval: {request_data.get(column.name)}")


def validate_datetime_masks(declarative_meta, request_data_object):
    if request.method != 'GET':
        declarative_meta_column_list = inspect(declarative_meta).columns
        for request_object in request_data_object:
            declarative_meta_item = get_declarative_meta_attribute_definitions(
                request_object, declarative_meta_column_list)
            if str(declarative_meta_item.type).lower() == 'timestamp' or str(declarative_meta_item.type).lower() == 'datetime':
                if isinstance(declarative_meta_item, timedelta) or str(declarative_meta_item.type.python_type).lower() == "<class 'datetime.timedelta'>":
                    validate_and_parse_interval(
                        declarative_meta_item, request_data_object)
                else:
                    validate_datetime(declarative_meta_item,
                                      request_data_object)
            if str(declarative_meta_item.type).lower() == 'date':
                validate_date(declarative_meta_item, request_data_object)
            if str(declarative_meta_item.type).lower() == 'time':
                validate_time(declarative_meta_item, request_data_object)



def get_declarative_meta_attribute_definitions(attribute, declarative_meta_attribute_list):
    for item in declarative_meta_attribute_list:
        if str(item.key) == str(attribute):
            return item


def validate_build(declarative_meta, request_data_object):
    try:
        build_domain_object_from_dict(
            declarative_meta, request_data_object
        )
    except Exception as e:
        raise Exception(str(e).replace(
            '__init__()', declarative_meta.__tablename__))


def cast_types_that_match(request_value, domain_value_type):
    match_types = {"float": "int"}
    if domain_value_type.__name__ in match_types:
        expected_type = match_types[domain_value_type.__name__]
        if type(request_value).__name__ == expected_type:
            casted_value = domain_value_type(request_value)
            return casted_value
        else:
            return None
    else:
        return None


def validate_python_type(declarative_meta, request_data_object):
    annotations = declarative_meta.__annotations__
    for key in request_data_object:
        if type(request_data_object[key]) != annotations[key]:
            casted_value = cast_types_that_match(
                request_data_object[key], annotations[key])
            if casted_value is not None:
                request_data_object[key] = casted_value
            else:
                raise Exception(
                    f"Expected type '{annotations[key]}' for attribute '{key}' "
                    f"but received type '{type(request_data_object[key])}'".replace(
                        "<class '", "").replace("'>", "")
                )


def validate_header_args(declarative_meta, header_args):
    validate_select_args(declarative_meta, header_args)
    validate_order_by(declarative_meta, header_args)
    validate_group_by(declarative_meta, header_args)


def validate_select_args(declarative_meta, header_args):
    if header_args.get('HTTP_SELECT') is not None:
        declarative_meta_attr = [str(key)
                                 for key in declarative_meta.schema.dump_fields]
        for key in header_args.get('HTTP_SELECT'):
            if key not in declarative_meta_attr and key != '':
                raise Exception(
                    f"{declarative_meta.__table__.name} select got an unexpected keyword argument '{key}'"
                )


def validate_order_by(declarative_meta, header_args):
    if header_args.get('HTTP_ORDERBY') is not None and header_args.get('HTTP_ORDERBY')[0] != '':
        if len(header_args.get('HTTP_ORDERBY')) == 2 or len(header_args.get('HTTP_ORDERBY')) == 1:
            if header_args.get('HTTP_ORDERBY')[0] not in [str(key) for key in declarative_meta.schema.dump_fields]:
                raise Exception(
                    f"orderby got an unexpected keyword argument '{header_args.get('HTTP_ORDERBY')[0]}'"
                )
        if len(header_args.get('HTTP_ORDERBY')) == 2:
            if header_args.get('HTTP_ORDERBY')[1] != 'asc' and header_args.get('HTTP_ORDERBY')[1] != 'desc':
                raise Exception(
                    f"'{header_args.get('HTTP_ORDERBY')[1]}' not a valid argument. Must be either 'asc' or 'desc'"
                )

def validate_group_by(declarative_meta, header_args):
    if header_args.get('HTTP_GROUPBY') is not None and header_args.get('HTTP_GROUPBY')[0] != '':
        if not len(header_args.get('HTTP_GROUPBY')) >= 1:
            if header_args.get('HTTP_GROUPBY')[0] not in [str(key) for key in declarative_meta.schema.dump_fields]:
                raise Exception(
                    f"groupby got an unexpected keyword argument '{header_args.get('HTTP_GROUPBY')[0]}'"
                )
        else:
            for header in header_args.get('HTTP_GROUPBY'):
                if header not in [str(key) for key in declarative_meta.schema.dump_fields]:
                    raise Exception(
                        f"groupby got an unexpected keyword argument '{header}'"
                    )
