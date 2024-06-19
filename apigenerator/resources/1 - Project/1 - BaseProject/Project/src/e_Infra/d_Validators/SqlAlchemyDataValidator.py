from src.e_Infra.b_Builders.DomainBuilder import *
from sqlalchemy.inspection import inspect
from datetime import datetime, timedelta
from flask import request
import re


def validate_request_data_object(declarative_meta, request_data_object):
    try:
        # Validate Builder attributes #
        validate_build(declarative_meta, request_data_object)
        # Validate Python types for attributes #
        validate_python_type(declarative_meta, request_data_object)
        # Custom validators #
        declarative_meta.validate_custom_rules(request_data_object)
        # Apply valid date/datetime/timestamp masks #
        validate_datetime_masks(declarative_meta, request_data_object)
    except Exception as e:
        raise e


def get_valid_datetime_masks():
    valid_datetime_masks = list()
    valid_date_masks = get_global_variable('date_valid_masks').split(',')
    valid_time_masks = get_global_variable('time_valid_masks').split(',')
    for i in range(len(valid_date_masks)):
        for j in range(len(valid_time_masks)):
            valid_datetime_masks.append(f'{valid_date_masks[i].strip()} {valid_time_masks[j].strip()}')
            valid_datetime_masks.append(f'{valid_date_masks[i].strip()}T{valid_time_masks[j].strip()}')
    return valid_datetime_masks


def validate_datetime(column, request_data):
    valid_datetime_masks = get_valid_datetime_masks()
    for datetime_mask in valid_datetime_masks:
        try:
            request_data[column.name] = datetime.strptime(request_data.get(column.name), datetime_mask.strip())
            return
        except Exception as e:
            del e
            continue
    raise Exception(f'Invalid datetime value for {column.name} attribute')


def validate_date(column, request_data):
    valid_date_masks = get_global_variable('date_valid_masks').split(',')
    for date_mask in valid_date_masks:
        try:
            request_data[column.name] = datetime.strptime(request_data.get(column.name), date_mask.strip())
            return
        except Exception as e:
            del e
            continue
    raise Exception(f'Invalid date value for {column.name} attribute')


def validate_time(column, request_data):
    valid_time_masks = get_global_variable('time_valid_masks').split(',')
    for time_mask in valid_time_masks:
        try:
            request_data[column.name] = datetime.strptime(request_data.get(column.name), time_mask.strip())
            return
        except Exception as e:
            del e
            continue
    raise Exception(f'Invalid time value for {column.name} attribute')


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
            declarative_meta_item = get_declarative_meta_attribute_definitions(request_object, declarative_meta_column_list)
            if str(declarative_meta_item.type).lower() == 'timestamp' or str(declarative_meta_item.type).lower() == 'datetime':
                if isinstance(declarative_meta_item, timedelta) or str(declarative_meta_item.type.python_type).lower() == "<class 'datetime.timedelta'>":
                    validate_and_parse_interval(declarative_meta_item, request_data_object)
                else:
                    validate_datetime(declarative_meta_item, request_data_object)
            if str(declarative_meta_item.type).lower() == 'date':
                validate_date(declarative_meta_item, request_data_object)
            if str(declarative_meta_item.type).lower() == 'time':
                validate_time(declarative_meta_item, request_data_object)


def get_declarative_meta_attribute_definitions(attribute, declarative_meta_attribute_list):
    for item in declarative_meta_attribute_list:
        if str(item.name) == str(attribute):
            return item


def validate_build(declarative_meta, request_data_object):
    try:
        build_domain_object_from_dict(
            declarative_meta, request_data_object
        )
    except Exception as e:
        raise Exception(str(e).replace('__init__()', declarative_meta.__tablename__))


def validate_python_type(declarative_meta, request_data_object):
    annotations = declarative_meta.__annotations__
    for key in request_data_object:
        if type(request_data_object[key]) != annotations[key]:
            raise Exception(
                f"Expected type '{annotations[key]}' for attribute '{key}' "
                f"but received type '{type(request_data_object[key])}'".replace("<class '", "").replace("'>", "")
            )


def validate_header_args(declarative_meta, header_args):
    validate_select_args(declarative_meta, header_args)
    validate_order_by(declarative_meta, header_args)


def validate_select_args(declarative_meta, header_args):
    if header_args.get('HTTP_SELECT') is not None:
        declarative_meta_attr = [str(key) for key in declarative_meta.schema.dump_fields]
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
