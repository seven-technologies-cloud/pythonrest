import shutil
import os
import sys
from pathlib import Path # Added
from string import Template # Added
from domaingenerator.DomainFilesGeneratorReplacer import *
from domaingenerator.DomainFilesGeneratorBuilder import *


def generate_domain_files(result_full_path, generated_domains_path):
    domain_list = get_domain_list(os.path.join(result_full_path, 'JSONMetadata'))

    # Determine script path and read mask template once before the loop
    try:
        script_absolute_path = define_script_path_based_on_run_context()
        # domain_mask_file_path can still use os.path for consistency with existing style if preferred for this line
        domain_mask_file_path = os.path.abspath(os.path.join(script_absolute_path, 'domaingenerator/DomainFilesGeneratorMask.py'))
        mask_content_string = Path(domain_mask_file_path).read_text()
        mask_template = Template(mask_content_string)
    except Exception as e:
        # Handle error in reading template or defining path, e.g., log and exit or raise
        print(f"Error preparing domain mask template: {e}")
        return # Or raise a custom exception

    for domain_file in domain_list:
        try:
            domain_dict = get_domain_dict(os.path.join(result_full_path, 'JSONMetadata', domain_file))
        except Exception as e:
            print(f"Error getting domain dict for {domain_file}: {e}")
            continue # Skip this domain file and try the next one

        try:
            domain_replacer = DomainFilesGeneratorReplacer(domain_dict)
        except Exception as e:
            print(f"Error creating replacer for {domain_file}: {e}")
            continue # Skip this domain file

        # build_domain_file now takes the pre-loaded template
        try:
            # The output filename will be determined in build_domain_file using domain_replacer.declarative_meta
            build_domain_file(mask_template, domain_replacer, generated_domains_path)
        except Exception as e:
            print(f"Error building domain file for {domain_replacer.declarative_meta if domain_replacer else domain_file}: {e}")
            continue # Skip this domain file

    # Cleanup JSONMetadata directory after processing all domain files
    try:
        if os.path.exists(os.path.join(result_full_path, 'JSONMetadata')): # Check existence before removal
            shutil.rmtree(os.path.join(result_full_path, 'JSONMetadata'))
    except Exception as e:
        print(f"Error removing JSONMetadata directory: {e}")

# Note: define_script_path_based_on_run_context() is assumed to be defined elsewhere
# and correctly returns the path to the script's directory or a base path for resources.
# Error handling within the loop now uses `continue` to skip problematic files
# rather than returning, allowing other domain files to be processed.
# Added more specific error messages.
# Added check for JSONMetadata existence before rmtree.
