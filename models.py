import datetime
import os
import peewee
from playhouse.db_url import connect
import markdown2

DB = connect(
  os.environ.get(
    'DATABASE_URL',
    'postgres://localhost:5432/blog'
    #5432 is the local post for postgres.
  )
)

class BaseModel (peewee.Model):
    class Meta:
        database = DB

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
#create blog db
#something called "migrations" peewee does a data migration
#so when you say "run the first migration" you're running a python file. It could also be a numbered sequal file.
#just make sure whatever you do here, when you go to dpeloy it you can do the same thing.
