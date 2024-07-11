# Builder Imports #
from src.e_Infra.b_Builders.DomainBuilder import *

# Infra Imports #
from src.e_Infra.CustomVariables import *


# Generic database transaction for selecting objects with argument options #
def select_all_objects(declarative_meta, request_args, session, header_args):
    try:
        # Invoking domain builder #
        query = build_query_from_api_request(
            declarative_meta, request_args, session, header_args, True
        )
        # Invoking ORM schema for JSON format result #
        return declarative_meta.schema.dumps(query)
    except Exception as e:
        session.rollback()
        raise e


# Generic database transaction for selecting objects by their id #
def select_object_by_id(declarative_meta, id_value_list, id_name_list, request_args, session, header_args):
    try:
        # Executing query according to existence of request_args parameter #
        if request_args != get_system_empty_dict() or header_args != get_system_empty_dict():
            query = build_query_from_api_request(
                declarative_meta, request_args, session, header_args
            )

            for i in range(len(id_value_list)):
                query = query.filter(getattr(declarative_meta, id_name_list[i]) == id_value_list[i])

        else:
            query = session.query(
                declarative_meta
            )
            for i in range(len(id_value_list)):
                query = query.filter(getattr(declarative_meta, id_name_list[i]) == id_value_list[i])
        # Invoking ORM schema for JSON format result #
        return declarative_meta.schema.dumps(query)
    except Exception as e:
        session.rollback()
        raise e


# Generic database transaction for inserting an object #
def insert_object(transaction_obj, session):
    try:
        # Executing insert query according to given transaction_obj #
        session.add(
            transaction_obj
        )
        # Returning session commit response #
        return session.commit()
    except Exception as e:
        session.rollback()
        raise e


# Generic database transaction for updating an object #
def update_object(declarative_meta, request_data, id_name_list, session):
    try:
        # Executing update query according to given id parameter #
        query = session.query(
            declarative_meta
        )
        for id_name in id_name_list:
            query = query.filter(
                getattr(
                    declarative_meta, id_name
                ) == request_data[id_name]
            )
        result = query.update(
            request_data
        )
        # Returning session commit response #
        session.commit()
        return result
    except Exception as e:
        session.rollback()
        raise e


# Generic database transaction for deleting an object #
def delete_object_by_id(declarative_meta, id_value_list, id_name_list, session):
    try:
        # Executing delete query according to given id parameter #
        query = session.query(
            declarative_meta
        )
        for i in range(len(id_value_list)):
            query = query.filter(getattr(declarative_meta, id_name_list[i]) == id_value_list[i])
        result = query.delete()
        # Returning session commit response #
        session.commit()
        # Returning number of fetched objects #
        return result
    except Exception as e:
        session.rollback()
        raise e


# Generic database transaction for deleting an object by providing all fields of the object table #
def delete_object_by_full_match(declarative_meta, request_data, session):
    try:
        query = build_query_from_api_request(
            declarative_meta, request_data, session
        )
        result = query.delete(
            synchronize_session='fetch'
        )
        session.commit()
        return result
    except Exception as e:
        session.rollback()
        raise e
