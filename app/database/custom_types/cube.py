import sqlalchemy.types as types


class Cube(types.UserDefinedType):
    def __init__(self):
        pass

    def get_col_spec(self, **kw):
        return "cube"

    def bind_processor(self, dialect):
        def process(value):
            return value
        return process

    def result_processor(self, dialect, coltype):
        def process(value):
            return value
        return process