import datetime
from sqlalchemy import orm
import sqlalchemy
from .db_session import SqlAlchemyBase
from .users import SerializerMixin

association_table = sqlalchemy.Table('association', SqlAlchemyBase.metadata,
                                     sqlalchemy.Column('jobs', sqlalchemy.Integer,
                                                       sqlalchemy.ForeignKey('jobs.id')),
                                     sqlalchemy.Column('category', sqlalchemy.Integer,
                                                       sqlalchemy.ForeignKey('category.id'))
                                     )


class Category(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'category'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
