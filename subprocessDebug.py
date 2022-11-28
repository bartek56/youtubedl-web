PIPE = -1
STDOUT = -2
DEVNULL = -3

class stdoutMock:
    stdout=[]

    # 0 - succesfull
    returncode=0

def run(*popenargs, input=None, capture_output=False, timeout=None, check=False, **kwargs):
    mock = stdoutMock()
    return mock

def check_output(*popenargs, timeout=None, **kwargs):
    return ["test1", "test2"]