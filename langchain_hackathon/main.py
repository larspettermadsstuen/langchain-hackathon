import os
import re
from langchain_hackathon.dbt_pydantic_models import Model
from langchain_hackathon.utils import get_yaml_file_paths, load_all_model_docs, load_field_descriptions, load_model_documentation_with_proper_field_docs, model_to_sorted_yaml
# get home folder into a variable:

MODELS_DIRECTORY_PATH = os.path.expanduser('~') + '/oda/dbt-models/snowflake/models'
FIELD_DOCUMENTATION_PATH = MODELS_DIRECTORY_PATH + '/field_documentation.md'




if __name__ == '__main__':
    # load models and
    raw_model_docs = load_all_model_docs(get_yaml_file_paths(MODELS_DIRECTORY_PATH))
    field_docs = load_field_descriptions(FIELD_DOCUMENTATION_PATH)

    all_model_docs = load_model_documentation_with_proper_field_docs(raw_model_docs, field_docs)

    dbt_model = Model(**all_model_docs['rbt_orders'])

    print(model_to_sorted_yaml(dbt_model))

