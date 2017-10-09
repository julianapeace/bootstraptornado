import models

def forward ():
    models.db.create_tables([models.Weather])

if __name__ == '__main__':
    forward()
