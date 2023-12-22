import shutil
import os
import sys
from domaingenerator.DomainFilesGeneratorReplacer import *
from domaingenerator.DomainFilesGeneratorBuilder import *


def generate_domain_files(result_full_path, generated_domains_path):
    domain_list = get_domain_list(os.path.join(result_full_path, 'JSONMetadata'))
    for domain_file in domain_list:

        try:
            domain_dict = get_domain_dict(os.path.join(result_full_path, 'JSONMetadata', domain_file))
        except Exception as e:
            print(e)
            return

        try:
            domain_replacer = DomainFilesGeneratorReplacer(domain_dict)
        except Exception as e:
            print(e)
            return

        try:
            script_absolute_path = define_script_path_based_on_run_context()
            domain_mask_file_path = os.path.abspath(os.path.join(script_absolute_path, 'domaingenerator/DomainFilesGeneratorMask.py'))
        except Exception as e:
            print(e)
            return

        try:
            build_domain_file(domain_mask_file_path, domain_replacer, generated_domains_path)
        except Exception as e:
            print(e)
            return

    shutil.rmtree(os.path.join(result_full_path, 'JSONMetadata'))
