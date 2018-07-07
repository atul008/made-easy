

class BaseConfig(object):
    PORT = 8090
    FKMP_TRACER_HOST = "http://10.85.59.15"
    MPCA_TRACER_HOST = "http://10.85.59.16"
    FKMP_MEDIATOR_HOST = "http://localhost:42120"
    MPCA_MEDIATOR_HOST = "http://localhost:42120"
    DEBUG = True
    TESTING = False


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = True


class TestingConfig(BaseConfig):
    DEBUG = False
    TESTING = True