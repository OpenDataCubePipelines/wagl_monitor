class Config(object):
    DEBUG = True
    TESTING = True

class Default(Config):
    DATABASE_URI = 'postgresql://av8534@localhost:5432/av8534'

class Test(Config):
    DATABASE_URI = 'postgresql://av8534@localhost:5432/av85342'
