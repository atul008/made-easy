"""
 * @author Atul Kumar , Date : 08/07/18

"""


class BaseConfig(object):
    PORT = 8090
    FKMP_TRACER_HOST = "http://hostname"
    MPCA_TRACER_HOST = "http://hostname"

    """Hosts for testing : """
    FKMP_MEDIATOR_HOST = "http://localhost"
    MPCA_MEDIATOR_HOST = "http://localhost"

    SQLALCHEMY_DATABASE_URI = "mysql://user:pass@hostname/db"

    """ @test_mediator_db : is used to  the mediator application db
    @prod_slave_db :  is used to get regression data """

    SQLALCHEMY_BINDS = {'test_mediator_db': 'mysql://user:pass@hostname/db',
        'prod_slave_db': 'mysql://user:pass@hostname/db'}

    DEBUG = True
    TESTING = False


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = True


class TestingConfig(BaseConfig):
    DEBUG = False
    TESTING = True
