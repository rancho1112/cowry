from PyQt5.QtCore import pyqtSignal, QObject
from core.baseSocket import BaseSocket
from core.upload import Upload
from core.download import Download
from core.config import Settings
from core.cryptogram import Cryptogram
from core import utils

class Signal(QObject):
    # def __init__(self):
    #     super(UploadSignal, self).__init__()
    refresh = pyqtSignal()
    # recv = pyqtSignal(int)

class FTPClient(BaseSocket):
    """docstring for FTPClient."""
    def __init__(self, **arg):
        super(FTPClient, self).__init__(**arg)
        self.signal = Signal()
        self.settings = Settings()
        self.crypt = Cryptogram()

        self.encryption = False
        self.encryption_type = None
        self.encryption_cipher = None
        self.upbar = None
        self.dpbar = None

    def login(self):
        self.log.info('start login')
        loginCmdCode = {'info': 'login', 'code': '1234', 'u': self.username, 'p': self.password}
        loginInfo = self.sendMsg(loginCmdCode)
        if loginInfo[0] == 1:
            self.log.info(loginInfo[1])
            return (1, loginInfo[1])

        recvInfo = self.recvMsg()
        if recvInfo[0] == 1:
            self.log.info(recvInfo[1])
            return (1, recvInfo[1])

        if self.recvInfo['status'] == '0':
            return (0, 'Login Successd', self.certInfo)
        else:
            return (1, self.recvInfo['reason'])

    def logout(self):
        self.log.info('start logout')
        logoutCmdCode = {'info': 'logout', 'code': ''}
        logoutInfo = self.sendMsg(logoutCmdCode)
        if logoutInfo[0] == 1:
            return (1,logoutInfo[1])

        recvInfo = self.recvMsg()
        if recvInfo[0] == 1:
            return (1, recvInfo[1])

        if self.recvInfo['status'] == '0':
            return (0, 'Logout Successd')
        else:
            return (1, self.recvInfo['reason'])
        self.clearCert()

    def reconnect(self):
        self.logout()

    # @encrypt
    def upload(self, filepath):
        filename = utils.getBaseNameByPath(filepath)
        filesize = utils.getSizeByPath(filepath)
        # check if need to encrypt files
        if self.encryption is True:
            retInfo = self.crypt.encrypt(str(self.encryption_cipher).strip(), filepath, mode= str(self.encryption_type).strip())
            if retInfo[0] == 0:
                enctryptedFilePath = retInfo[1]
            else:
                return (1, retInfo[1])
            encryptedFileSize = utils.getSizeByPath(enctryptedFilePath)

            fileHashCode = utils.calculateHashCodeForFile(enctryptedFilePath)
            uploadCmdCode = {'info': "upload",
                             "code": "",
                             "filename": filename,
                             "filesize": filesize,
                             "encryption": "1",
                             "encsize": encryptedFileSize,
                             "encryption_type": self.encryption_type,
                             "hash": fileHashCode }
        else:

            fileHashCode = utils.calculateHashCodeForFile(filepath)
            uploadCmdCode = {'info': "upload",
                             "code": "",
                             "filename": filename,
                             "filesize": filesize,
                             "encryption": "0",
                             "encryption_type": "0",
                             "encsize": "0",
                             "hash": fileHashCode }

        uploadInfo = self.sendMsg(uploadCmdCode)
        if uploadInfo[0] == 1:
            self.log.info(uploadInfo[1])
        else:
            retInfo = self.recvMsg()
            if retInfo[0] == 1:
                return (1, retInfo[1])
            elif self.recvInfo['status'] == '0':
                uploadAuthCode = self.recvInfo['token']
                remoteDataInfo = self.recvInfo['dataAddress']
                self.log.info('recv upload auth token is : {}'.format(uploadAuthCode))
                self.log.info('remote open data info : {}:{}'.format(remoteDataInfo[0],remoteDataInfo[1]))

                if self.encryption:
                    filepath = enctryptedFilePath

                self.uploadProcess = Upload(remoteDataInfo, filepath, uploadAuthCode)
                self.uploadProcess.signal.p.connect(self.setUpbarValue)
                self.uploadProcess.start()

                return (0, 'ok')
            else:
                return (1, self.recvInfo['reason'])
        # uploadProcess = Upload()

    # @decrypt
    def download(self, filename, savefilepath, decryption_type=None):
        # filename = os.path.basename(filepath)
        # filesize = os.path.getsize(filepath)
        # try:
        #     with open(filepath, 'rb') as f:
        #         fileHashCode = hashlib.md5(f.read()).hexdigest()
        # except Exception as e:
        #     return (1, str(e))
        downloadCmdCode = {'info': 'download', 'code': '', 'filename': filename}
        retInfo = self.sendMsg(downloadCmdCode)
        if retInfo[0] == 1:
            self.log.info(retInfo[1])
        else:
            retInfo = self.recvMsg()
            if retInfo[0] == 1:
                return (1, retInfo[1])
            elif self.recvInfo['status'] == '0':
                downloadAuthCode = self.recvInfo['token']
                remoteDataInfo = self.recvInfo['dataAddress']
                fileHashCode = self.recvInfo['fileinfo']['hashcode']

                if decryption_type != None:
                    saveFilePath = utils.joinFilePath('/tmp/', filename + 'enc')
                    fileSize = self.recvInfo['fileinfo']['encsize']
                    decryptInfo = {
                        "encryption_type": self.encryption_type,
                        "cipher": self.encryption_cipher,
                        "savefilepath": savefilepath
                    }
                else:
                    saveFilePath = savefilepath
                    fileSize = self.recvInfo['fileinfo']['size']
                    decryptInfo = None
                self.log.info('recv download auth token is : {}'.format(downloadAuthCode))
                self.log.info('remote open data info : {}:{}'.format(remoteDataInfo[0],remoteDataInfo[1]))
                self.downloadProcess = Download(remoteDataInfo, saveFilePath, downloadAuthCode, fileHashCode, fileSize, decrypt_info= decryptInfo)
                # print(self.uploadProcess.__dict__)
                self.downloadProcess.signal.p.connect(self.setDpbarValue)
                self.downloadProcess.start()

                return (0, 'ok')
            else:
                return (1, self.recvInfo['reason'])
        # uploadProcess = Upload()

    def setUpbarValue(self, progress):
        self.upbar.ui.Progress.setValue(progress[0])
        self.upbar.ui.Percentage_label.setText(progress[1])

    def setDpbarValue(self, progress):
        self.dpbar.ui.Progress.setValue(progress[0])
        self.dpbar.ui.Percentage_label.setText(progress[1])

    def uploadComfirm(self):
        uploadComfirmCmdCode = {'info': 'uploadComfirm', 'code': '', 'status': '0'}
        self.sendMsg(uploadComfirmCmdCode)
        self.upbar.close()
        self.signal.refresh.emit()

    def downloadComfirm(self):
        self.dpbar.close()

    def refresh(self, folder):
        return self.list(folder)

    def list(self, folder= '/'):
        listCmdCode = {'info': 'list', 'code': '', 'dir': folder}
        try:
            self.sendMsg(listCmdCode)
        except Exception as e:
            return (1, str(e))

        try:
            self.recvMsg()
        except Exception as e:
            self.log.info(str(e))
            return (1, str(e))
        else:
            return (0, self.recvInfo['list'])
