from domaingenerator.DomainFilesGeneratorDTOReplacer import *


class DomainFilesGeneratorReplacer:
    def __init__(self, domain_dict):

        self.domain_imports = 'import ujson\n'
        self.declarative_meta = domain_dict['ClassName']
        self.meta_string = domain_dict['TableName']
        self.columns_names = get_columns_names_str(domain_dict)
        self.sa_columns = get_sa_columns(domain_dict)
        self.columns_init = get_columns_init(domain_dict)
        self.self_columns = get_self_columns(domain_dict)
