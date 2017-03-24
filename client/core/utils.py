import os, hashlib, random, _thread
from ast import literal_eval

def prettySize(num, suffix='B'):
    num = int(num)
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "{:.3f} {}{}".format(num, unit, suffix)
        num /= 1024.0

def getSizeByPath(filepath):
    return os.path.getsize(filepath)

def getBaseNameByPath(filepath):
    return os.path.basename(filepath)

def calculateHashCodeForFile(filepath):
    try:
        with open(filepath, 'rb') as f:
            fileHashCode = hashlib.md5(f.read()).hexdigest()
    except Exception as e:
        return (1, str(e))
    return fileHashCode

def generateRandomDigitFromRange(start, end):
    return random.randrange(start, end)

def rebuildDictFromBytes(bytes):
    return literal_eval(bytes.decode('utf8'))

def startNewThread(work, params= ()):
    if params:
        _thread.start_new_thread(work, params)
    else:
        _thread.start_new_thread(work, ())

def delfolder(folderpath):
    shutil.rmtree(folderpath)

def generateAuthToken():
    return uuid.uuid4().hex.upper()

def getCurrentTime():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

def joinFilePath(*params):
    params = [x for x in params]
    return os.path.join(*params)

def deleteFile(filepath):
    os.remove(filepath)

def getenv(name):
    return os.getenv(name)

def setenv(name, value):
    os.environ[name] = str(value)

def delfolder(folderpath):
    shutil.rmtree(folderpath)

def checkFileExists(filepath):
    return os.path.isfile(filepath)

def verifyDomain(domain):
    reg = '^[a-z0-9]([a-z0-9-]+\.){1,}[a-z0-9]+\Z'
    return re.search(reg, domain)

def getHostAddr():
    return socket.gethostbyname(socket.gethostname())
