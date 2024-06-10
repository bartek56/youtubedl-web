import random
import string
import os
import zipfile
from flask import render_template

def alert_info(info):
    return render_template('alert.html', alert=info)

def getRandomString():
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(8))
    return result_str

def isFile(file):
    return os.path.isfile(file)

def compressToZip(files, playlistName):
    # TODO zip fileName
    zipFileName = "%s.zip"%playlistName
    zipFileWithPath = os.path.join("/tmp/quick_download", zipFileName)
    with zipfile.ZipFile(zipFileWithPath, 'w') as zipf:
        for file_path in files:
            arcname = file_path.split("/")[-1]
            zipf.write(file_path, arcname)
    return zipFileName
