
import sqlalchemy as sa
from sqlalchemy.ext import declarative
from sqlalchemy import orm 

import settings


_Base = declarative.declarative_base()
_inited = False
_db = None


class Function(_Base):
    __tablename__ = 'function'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    file_name = sa.Column(sa.String)
    lineno = sa.Column(sa.Integer)
    
    type = sa.Column(sa.String)

    __mapper_args__ = {
        'polymorphic_identity': 'function',
        'polymorphic_on': type,
    }


# TODO(nathan): Actually use this.
class QualifiedFunction(Function):
    __tablename__ = 'qualified_function'

    id = sa.Column(sa.Integer, sa.ForeignKey('function.id'), primary_key=True)
    class_name = sa.Column(sa.String)
    module_name = sa.Column(sa.String)

    @property
    def full_name(self):
        name_parts = (self.module_name, self.class_name, self.function_name)
        return '.'.join(
            name for name in name_parts if name is not None)

    __mapper_args__ = {
        'polymorphic_identity': 'qualified_function',
    }


class AnonymousFunction(Function):
    __tablename__ = 'anonymous_function'

    id = sa.Column(sa.Integer, sa.ForeignKey('function.id'), primary_key=True)

    @property
    def full_name(self):
        return 'Anonymous function "{}" defined at {}:{}'.format(
            self.function_name, self.file_name, self.lineno)

    __mapper_args__ = {
        'polymorphic_identity': 'anonymous_function',
    }


class Return(_Base):
    __tablename__ = 'return'

    id = sa.Column(sa.Integer, primary_key=True)
    function_id = sa.Column(sa.Integer, sa.ForeignKey('function.id'))
    function = orm.relationship('Function')
    type_name = sa.Column(sa.String)


class Arg(_Base):
    __tablename__ = 'arg'

    id = sa.Column(sa.Integer, primary_key=True)
    function_id = sa.Column(sa.Integer, sa.ForeignKey('function.id'))
    function = orm.relationship('Function')
    arg_name = sa.Column(sa.String)
    type_name = sa.Column(sa.String)




def _init_models(engine):
    global _inited
    if _inited:
        return
    _Base.metadata.create_all(engine)
    _inited = True


def get_db():
    global _db
    if not _db:
        _db = _Db()
    return _db


def get_session():
    return get_db().session


class _Db(object):

    def __init__(self):
        self._engine = sa.create_engine(settings.get('engine'))
        _init_models(self._engine)
        self._session_cls = orm.sessionmaker(bind=self._engine)
        self.connection = self._engine.connect()
        self.session = self._session_cls(bind=self.connection)

    def reset(self):
        self.connection.close()
        self.session.close()

        self.connection = self._engine.connect()
        self.session = self._session_cls(bind=self.connection)
