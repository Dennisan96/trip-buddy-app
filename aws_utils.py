import os

def is_on_beanstalk():
    return os.getenv('AWS_EXECUTION_ENV') is not None