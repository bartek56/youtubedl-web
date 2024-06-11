import os

class Config:
    SECRET_KEY = "super_extra_key"
    SESSION_TYPE = "filesystem"
    SESSION_PERMANENT = True

class ConfigTesting:
    SECRET_KEY = "super_extra_key"
    SESSION_TYPE = "filesystem"
    SESSION_PERMANENT = True
    TESTING = True