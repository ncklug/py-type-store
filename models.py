
import sqlalchemy as sa
from sqlalchemy.ext import declarative
from sqlalchemy import orm 

import settings


_Base = declarative.declarative_base()
_inited = False
_db = None


class Return(_Base):
    __tablename__ = 'return'

    id = sa.Column(sa.Integer, primary_key=True)
    function_name = sa.Column(sa.String)
    type_name = sa.Column(sa.String)


class Arg(_Base):
    __tablename__ = 'arg'

    id = sa.Column(sa.Integer, primary_key=True)
    function_name = sa.Column(sa.String)
    arg_name = sa.Column(sa.String)
    type_name = sa.Column(sa.String)


class Assign(_Base):
    __tablename__ = 'assign'

    id = sa.Column(sa.Integer, primary_key=True)
    module_name = sa.Column(sa.String)
    lineno = sa.Column(sa.Integer)
    var_name = sa.Column(sa.String)
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
