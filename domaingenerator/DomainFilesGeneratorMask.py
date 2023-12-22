# Domain Imports #
${domain_imports}
# ${declarative_meta} Validator Import #
from src.e_Infra.d_Validators.a_Domain.${declarative_meta}Validator import *

# SqlAlchemy Import #
from src.e_Infra.b_Builders.SqlAlchemyBuilder import *


# SqlAlchemy ${declarative_meta} domain schema #
class ${declarative_meta}Schema(SQLAlchemySchema):
    class Meta:
        json_module = ujson
        ordered = True
        fields = (${columns_names})


# SqlAlchemy ${declarative_meta} domain class #
class ${declarative_meta}(Base):
    __tablename__ = "${meta_string}"
${sa_columns}
    def __init__(self${columns_init}):
${self_columns}
    # SqlAlchemy ${declarative_meta} JSON schema #
    schema = ${declarative_meta}Schema(many=True)

    # Custom ${declarative_meta} validators #
    validate_custom_rules = validate_${meta_string}
