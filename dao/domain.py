from infra.mysql import Model, StringField

# Sample ORM
class User(Model):
    __table__ = 'user'

    open_id = StringField(primary_key=True)
    user_name = StringField()