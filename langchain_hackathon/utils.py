import re
from typing import List
import os

import yaml

from langchain_hackathon.dbt_pydantic_models import Model

def get_yaml_file_paths(models_directory_path: str) -> List[str]:
    '''
    Parameters:
    models_directory_path(str): Absolute path to the directory containing dbt models,
    and schema definitions.

    Returns:
    List[str]: Returns the absolute path to yaml fields found with the models_directory,
    found by recursive search.
    '''

    yaml_file_paths = []

    for root, dirs, files in os.walk(models_directory_path):
        for f in files:
            if os.path.splitext(f)[1] in ('.yml', '.yaml'):
                yaml_file_paths.append(os.path.join(root, f))

    return yaml_file_paths


def load_field_descriptions(file_path):
    all_docs = {}
    pattern = r"\{%\s*docs\s*(\w+)\s*%\}(.*?)\{%\s*enddocs\s*%\}"
    with open(file_path, 'r') as field_docs:
        for l in field_docs:
            #print(l)
            match = re.search(pattern, l)
            if match:
                key = str(match.group(1))
                value = str(match.group(2).strip())
                all_docs[key] = value

    return all_docs

def load_all_model_docs(yaml_file_path_list: List[str]):
    all_model_docs = {}
    for yaml_file_path in yaml_file_path_list:
        #print(f"loading {yaml_file_path}")
        with open(yaml_file_path) as f:

            schema_dict = yaml.load(f, Loader=yaml.FullLoader)

            # Ignore empty files
            if schema_dict is None:
                continue

            for model in schema_dict.get('models', {}):
                all_model_docs[model['name']] = model

    return all_model_docs

def model_to_sorted_yaml(dbt_model: Model) -> str:

    dbt_model_dict = dbt_model.model_dump()
    # Define your custom sort order here
    key_order = ['name', 'meta', 'description', 'columns']

    def sort_dict(d):
        # Remove None values
        d = {k: v for k, v in d.items() if v is not None}

        # Sort the dictionary by key order
        sorted_items = sorted(d.items(),
                            key=lambda i: key_order.index(i[0]) if i[0] in key_order else len(key_order))
        return dict(sorted_items)

    def deep_sort_dict(d):
        if isinstance(d, list):
            return [deep_sort_dict(item) for item in d]
        elif isinstance(d, dict):
            return {k: deep_sort_dict(v) for k, v in sort_dict(d).items()}
        return d

    def represent_ordered_dict(dumper, data):
        return dumper.represent_mapping('tag:yaml.org,2002:map', data.items())


    sorted_data = deep_sort_dict(dbt_model_dict)

    # Convert to YAML
    yaml.add_representer(dict, represent_ordered_dict, Dumper=yaml.SafeDumper)

    # Convert to YAML
    yaml_str = yaml.safe_dump(sorted_data)


    return yaml_str

def load_model_documentation_with_proper_field_docs(model_docs, field_docs):
    # Load the field documentation and replace the docstring references with the actual docstrings
    pattern = r'\{\{\s*doc\("([^"]+)"\)\s*\}\}'
    for _, docs in model_docs.items():
        if 'columns' in docs:
            for col in docs['columns']:
                if 'description' in col:
                    match = re.search(pattern, col['description'])
                    if match:
                        key = match.group(1)
                        if key in field_docs:
                            col['description'] = field_docs[key]

    return model_docs
