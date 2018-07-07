from enum import Enum
from Config import BaseConfig


class BU(Enum):
    def __new__(cls, *args, **kwds):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, tracer_url, mediator_url):
        self.tracer_url = tracer_url
        self.mediator_url = mediator_url

    FKMP = BaseConfig.FKMP_TRACER_HOST + "/tracer/search?row_key=",  BaseConfig.FKMP_MEDIATOR_HOST + "/events/FKMP/process"
    MPCA = BaseConfig.MPCA_TRACER_HOST + "/tracer/search?row_key=",  BaseConfig.MPCA_MEDIATOR_HOST + "/events/MPCA/process"
