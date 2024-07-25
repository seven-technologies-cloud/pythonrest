# SqlAlchemy Imports
from sqlalchemy import inspect, func, Time, extract

# Resolver Imports #
from src.e_Infra.c_Resolvers.SqlAlchemyStringFilterResolver import *

# Builder Imports #
from src.e_Infra.b_Builders.DomainObjectBuilder import build_domain_object_from_dict

# Variables Imports #
from src.e_Infra.GlobalVariablesManager import *
from src.e_Infra.b_Builders.StringBuilder import *
import datetime
import re
from src.e_Infra.d_Validators.SqlAlchemyDataValidator import validate_date, validate_datetime, validate_time, validate_year, validate_year_month


# Method builds a domain object from a dictionary #
def build_domain_object_from_dict(declarative_meta, dictionary):
    # Remove keys with null values #
    remove_keys_with_null_values(dictionary)
    # Assigning dictionary to __init__ class method #
    class_object = declarative_meta(**dictionary)
    # Returning construct object #
    return class_object


# Method builds a domain query filter object from standard or custom definitions #
def build_query_from_api_request(declarative_meta, request_args, session, header_args=None, limit=False):
    # Building select for query args #
    query_args = get_select_query_args(header_args, declarative_meta)
    # Initializing query session by declarative_meta param #
    query = session.query(*query_args)
    # Building class object from given param request_args #
    class_object = build_domain_object_from_dict(
        declarative_meta, request_args)
    # Iterating over instantiated class object to resolve filter #
    for attr in class_object.__dict__:
        # Removing SqlAlchemy's _sa_instance_state attribute from validation  #
        if attr != '_sa_instance_state':
            if attr in request_args:  # Check if the attribute is in request_args
                value = getattr(class_object, attr)
                # Check if the value is NULL or null (case-insensitive)
                if str(value).lower() in ('null', 'null'):
                    query = query.filter(
                        getattr(declarative_meta, attr) == None)
                else:
                    # Checking if in global list for left-sided like filter #
                    if str(getattr(declarative_meta, attr)) in get_global_variable('domain_like_left').replace(' ', '').split(','):
                        query = resolve_string_filter(
                            declarative_meta, class_object, attr, query, 'left_like')
                    # Checking if in global list for right-sided like filter #
                    elif str(getattr(declarative_meta, attr)) in get_global_variable('domain_like_right').replace(' ', '').split(','):
                        query = resolve_string_filter(
                            declarative_meta, class_object, attr, query, 'right_like')
                    # Checking if in global list for full like filter #
                    elif str(getattr(declarative_meta, attr)) in get_global_variable('domain_like_full').replace(' ', '').split(','):
                        query = resolve_string_filter(
                            declarative_meta, class_object, attr, query, 'full_like')
                    # Not in any global list for like filter #
                    else:
                        if request_args:
                            for key, query_param in request_args.items():
                                if '[to]' in query_param.lower():
                                    # Apply filter by interval datetime #
                                    query = apply_query_filter_datetime(
                                        query, query_param, key, declarative_meta)
                                else:
                                    query = resolve_string_filter(
                                        declarative_meta, class_object, attr, query, 'regular')

    # Apply order by to query #
    query = query_order_by(query, header_args, declarative_meta)
    # Apply pagination to query #
    query = apply_query_offset(query, header_args)
    # Apply limit to query #
    query = apply_query_limit(query, header_args, limit)
    # Returning filtered query #
    return query


def query_order_by(query, header_args, declarative_meta):
    header_args = dict() if header_args is None else header_args
    if header_args.get('HTTP_ORDERBY') is not None and header_args.get('HTTP_ORDERBY')[0] != '':
        if len(header_args.get('HTTP_ORDERBY')) == 2:
            if header_args['HTTP_ORDERBY'][1] == 'asc':
                query = query.order_by(
                    getattr(declarative_meta, header_args['HTTP_ORDERBY'][0]))
            else:
                query = query.order_by(
                    getattr(declarative_meta, header_args['HTTP_ORDERBY'][0]).desc())
        else:
            query = query.order_by(
                getattr(declarative_meta, header_args['HTTP_ORDERBY'][0]))
    return query


def apply_query_limit(query, header_args, limit):
    if limit:
        header_args = dict() if header_args is None else header_args
        limit_value = header_args.get('HTTP_LIMIT')
        limit_value = limit_value if limit_value is not None else get_global_variable(
            'query_limit')
        if limit_value == '*':
            return query
        else:
            query = query.limit(int(limit_value))
    return query


def apply_query_filter_datetime(query, query_param, key, declarative_meta):
    column_attributes = [getattr(declarative_meta, col.name)
                         for col in declarative_meta.__table__.columns]
    if query_param.count("[to]") == 1:
        start_and_end_dates = re.sub(
            r'\s+\[to\]\s+', '[to]', query_param).split('[to]')
        for field in column_attributes:
            if field.name == key:
                start_datetime, end_datetime = start_and_end_dates
                if field.type.python_type in (
                    datetime.date, datetime.datetime, datetime.time, datetime.datetime.timestamp, datetime.date.year
                ):
                    date_type = validate_all_datetime_types(field,
                                                            start_and_end_dates)
                    if date_type == 'time':
                        query = query.filter(func.cast(field, Time).between(
                            start_datetime, end_datetime))
                    elif date_type == 'year':
                        query = query.filter(func.year(field).between(
                            int(start_datetime), int(end_datetime)))
                    elif date_type == 'year-month':
                        start_year, start_month = start_datetime.split('-')
                        end_year, end_month = end_datetime.split('-')
                        query = query.filter(extract('year', field).between(
                            int(start_year), int(end_year)), extract('month', field).between(int(start_month), int(end_month)))
                    else:
                        query = query.filter(
                            field.between(str(start_datetime), str(end_datetime)))
                        return query
                else:
                    date_type = validate_all_datetime_types(field,
                                                            start_and_end_dates)
                    if date_type == 'year':
                        query = query.filter(
                            field >= str(start_datetime), field <= str(end_datetime))
                        return query
                    else:
                        raise Exception(
                            f"[to] is not supported on given query param"
                        )
    else:
        raise Exception(
            f"datetime filter invalid, can only contain one [to]"
        )
    return query


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
            validate_year(column, data)
            return 'year'
        except Exception:
            pass

        try:
            validate_year_month(column, data)
            return 'year-month'
        except Exception:
            pass
    raise Exception(
        f'Failed to validate {column.name} as datetime, date, or time')


def apply_query_offset(query, header_args):
    header_args = dict() if header_args is None else header_args
    if header_args.get('HTTP_PAGE') is not None:
        if header_args.get('HTTP_LIMIT') is not None:
            # header_args = dict() if header_args is None else header_args
            page = header_args.get('HTTP_PAGE')
            limit = header_args.get('HTTP_LIMIT')

            query = query.offset((page-1)*limit)
        else:
            raise Exception(
                f"page header can't be defined without limit header"
            )
    return query


# Method builds an error message from an object and an exception error cause #
def build_object_error_message(object_from_body, validation_error):
    # Constructing empty dictionary object #
    error_dict = dict()
    # Populating body #
    error_dict['body'] = object_from_body
    # Populating error #
    error_dict['error'] = validation_error
    # Returning error object #
    return error_dict


def remove_keys_with_null_values(dictionary):
    keys_to_delete = list()
    for key in dictionary:
        if dictionary[key] is None:
            keys_to_delete.append(key)
    for key_to_delete in keys_to_delete:
        del dictionary[key_to_delete]


def fill_missing_keys_with_null_values(declarative_meta, dictionary):
    dictionary = build_domain_object_from_dict(
        declarative_meta, dictionary).__dict__
    del dictionary['_sa_instance_state']


def auto_fill_guid_in_request_body(declarative_meta, dictionary):
    auto_fill_guid_allowed_types = {'CHAR(36)', 'UUID'}
    ins = inspect(declarative_meta)
    for column in ins.tables[0].columns:
        if column.primary_key:
            if column.name not in dictionary:
                if str(column.type) in auto_fill_guid_allowed_types:
                    dictionary[column.name] = generate_guid()


def get_select_query_args(header_args, declarative_meta):
    header_args = dict() if header_args is None else header_args
    query_args = list()
    select_args = header_args.get('HTTP_SELECT')
    if select_args is not None:
        for key in select_args:
            if key != '':
                query_args.append(getattr(declarative_meta, key))
    if query_args == list():
        query_args.append(declarative_meta)
    return query_args


def cast_request_args(request_args, declarative_meta):
    for key, value in request_args.items():
        if hasattr(declarative_meta, key):
            cast = declarative_meta.__annotations__[key]
            value = apply_custom_cast(cast, key, value)
            request_args[key] = cast(value)


def apply_custom_cast(cast, key, value):
    if cast == bool:
        if value.lower() == 'false':
            value = False
        elif value.lower() == 'true':
            value = True
        elif value.lower() == '0':
            value = False
        elif value.lower() == '1':
            value = True
        else:
            raise Exception(
                f"Expected type '{bool}' for attribute '{key}'"
            )

    return value


def cast_headers_args(header_args):
    if header_args.get('HTTP_SELECT') is not None:
        header_args['HTTP_SELECT'] = header_args['HTTP_SELECT'].replace(
            ' ', '').split(',')

    if header_args.get('HTTP_ORDERBY') is not None:
        header_args['HTTP_ORDERBY'] = header_args['HTTP_ORDERBY'].replace(
            ' ', '').split(',')

    if header_args.get('HTTP_LIMIT') is not None:
        if header_args['HTTP_LIMIT'] == '*':
            return
        try:
            header_args['HTTP_LIMIT'] = int(header_args['HTTP_LIMIT'])
        except Exception:
            raise Exception(
                f"'{header_args['HTTP_LIMIT']}' is not an integer"
            )

    if header_args.get('HTTP_PAGE') is not None:
        try:
            header_args['HTTP_PAGE'] = int(header_args['HTTP_PAGE'])
        except Exception:
            raise Exception(
                f"'{header_args['HTTP_PAGE']}' is not an integer"
            )
