import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from sqlalchemy import Column, Integer, String

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UserModel(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    last_name = Column(String)


class User(SQLAlchemyObjectType):
    class Meta:
        model = UserModel
        # use `only_fields` to only expose specific fields ie "name"
        # only_fields = ("name",)
        # use `exclude_fields` to exclude specific fields ie "last_name"
        # exclude_fields = ("last_name",)

class Query(graphene.ObjectType):
    users = graphene.List(User)

    def resolve_users(self, info):
        query = User.get_query(info)  # SQLAlchemy query
        return query.all()

schema = graphene.Schema(query=Query)

query = '''
    query {
      users {
        name,
        lastName
      }
    }
'''
result = schema.execute(query, context_value={'session': db_session})