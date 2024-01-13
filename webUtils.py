import random
import string
import os
from flask import render_template

def alert_info(info):
    return render_template('alert.html', alert=info)

def getRandomString():
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(8))
    return result_str

def isFile(file):
    return os.path.isfile(file)