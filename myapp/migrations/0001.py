import models

def forward ():
    models.DB.create_tables([models.BlogPost])
  #when we use "create_tables" Peewee will translate the model and create the table for us.
if __name__ == '__main__':
    forward()
