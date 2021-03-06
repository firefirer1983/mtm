from decimal import Decimal

import sqlalchemy.types as types


class SqliteNumeric(types.TypeDecorator):
    impl = types.String
    
    def __init__(self, precision):
        super().__init__()
        self._precision = precision
        
    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(types.VARCHAR(100))
    
    def process_bind_param(self, value, dialect):
        return str(value)
    
    def process_result_value(self, value, dialect):
        return Decimal(value)


# can overwrite the imported type name
# @note: the TypeDecorator does not guarantie the scale and precision.
# you can do this with separate checks
Numeric = SqliteNumeric
