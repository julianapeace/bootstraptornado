import datetime
import os
import peewee
from playhouse.db_url import connect
from playhouse.postgres_ext import *
import markdown2

DB = connect(
  os.environ.get(
    'DATABASE_URL',
    'postgres://localhost:5432/weatherapp'
    #5432 is the local post for postgres.
  )
)

db = PostgresqlExtDatabase('weatherapp', server_side_cursors=False, register_hstore=False)

class BaseModel (peewee.Model):
    class Meta:
        database = db

class Author (BaseModel):
    name = peewee.CharField(max_length=60)
    twitter = peewee.CharField(max_length=60)

    def __str__ (self):
        return self.name

class BlogPost (BaseModel):
    author = peewee.ForeignKeyField(Author, null=True)#we are joining author table with blogpost with foreignkey

    title = peewee.CharField(max_length=60)
    slug = peewee.CharField(max_length=50, unique=True)

    #a slug is a newspaper term. blog posts and video sites have a unique pretty URL briefly describing the page
    #ID is created automatically

    body = peewee.TextField()
    created = peewee.DateTimeField(
              default=datetime.datetime.utcnow)

    def __str__ (self):
        return self.title
        #if you ever have to print(post) it wont return something non-human friendly. good idea to print something unique like an id. useful for IT support on your app.
    def html(self):
        return markdown2.markdown(self.body)

class Weather (BaseModel):
    name = peewee.CharField(max_length=60)
    response = BinaryJSONField()
    created = peewee.DateTimeField(
              default=datetime.datetime.utcnow)

    def __str__ (self):
        return self.city_name
