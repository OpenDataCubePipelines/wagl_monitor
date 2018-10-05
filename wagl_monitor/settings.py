class BaseConfig(object):
    DEBUG = False
    TESTING = False
    DATABASE_URI = 'postgresql://localhost:5432/av8534'


class DevelopConfig(BaseConfig):
    TESTING = True
    DEBUG = True
    DATABASE_URI = 'postgresql://localhost:5432/monitor_ci'


class TestConfig(DevelopConfig):
    DEBUG = False


class DefaultConfig(BaseConfig):
    DATABASE_URI = 'postgresql://localhost:5432/wagl_monitor'
