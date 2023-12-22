from parse import parse
from apigenerator.e_Enumerables.Enumerables import *
from apigenerator.a_Domain.SaRowAttribute import *
from apigenerator.g_Utils.OpenFileExeHandler import open


class SaMetaClassAttributes:

    def __init__(self, declarative_meta, meta_string, attr_list):
        self.declarative_meta = declarative_meta
        self.meta_string = meta_string
        self.attr_list = attr_list


def get_sa_meta_class_attributes_object(domain_path, domain):
    with open(('{}/{}'.format(domain_path, domain)), 'r') as py_file:
        content = py_file.readlines()
        attr_list = list()
        for line in content:

            if "class" in line and "(Base)" in line:
                # --------------------- OBJECT ATTR --------------------- #
                declarative_meta = list(parse('class {}(Base){}', line))[0].strip()

            if "__tablename__" in line:
                # --------------------- OBJECT ATTR --------------------- #
                meta_string = list(parse('{}={}', line))[1].strip().replace('"', '').replace("'", '')

            if 'sa.Column' in line:
                # --------------------- OBJECT ATTR --------------------- #
                row_attr = list(parse('{}:{}={}', line))[0].strip()

                attr_params = list(parse('{}sa.Column({})\n', '{}\n'.format(line.strip())))[1].split(',')

                attr_object = get_sa_row_attr_object(row_attr, attr_params)
                attr_list.append(attr_object)

        sa_meta_class_attributes_obj = SaMetaClassAttributes(declarative_meta, meta_string, attr_list)

        return sa_meta_class_attributes_obj
