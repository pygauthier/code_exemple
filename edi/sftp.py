import os
import glob
from pathlib import Path

import settings

from libraries.sftp import SFTP as SFTPSUPER

from models.Mongo.edimsss import EDIMSSSLogs, EDIMSSSDocuments

from libraries.utilities import Utilities as Util

from env import (
    EDIMSSS_SFTP_HOST, EDIMSSS_SFTP_PASSWORD, 
    EDIMSSS_SFTP_PORT, EDIMSSS_SFTP_USERNAME,
    env
)

if env == 'dev':
    EDIMSSS_SFTP_HOST = '45.62.249.219'

class SFTP(SFTPSUPER):

    def __init__(self) -> None:
        self.log_path = "logs/EDIMSSS_SFTP.log"
        super().__init__()

        # login
        self.host = EDIMSSS_SFTP_HOST
        self.port = EDIMSSS_SFTP_PORT
        self.username = EDIMSSS_SFTP_USERNAME
        self.password = EDIMSSS_SFTP_PASSWORD

        # PATH
        self.remote_upload_path = './inbound'
        self.remote_download_path = './outbound'

        self.local_path = f'{settings.storage}/edimsss'
        self.local_download_path = f"{self.local_path}/inbound"
        self.local_upload_path = f"{self.local_path}/outbound"
        self.local_upload_process_path = f"{self.local_upload_path}/process/{self.date}"
        self.local_process_path = f"{self.local_download_path}/process/{self.date}"

    def _list_remote_file(self, dir:str=".") -> list:
        if not hasattr(self, 'sftp'):
            self.connect()
        return [i for i in self.sftp.listdir(dir)]

    def _list_local_file(self, dir:str=".") -> list:
        return [
            f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))
        ]

    def get_files(self):
        self.connect()
        results = {'transfert':[]}
        errors = []
        files = self._list_remote_file(self.remote_download_path)
        for file in files:
            file_name = file
            self.sftp.get(
                f"{self.remote_download_path}/{file}",
                f"{self.local_download_path}/{file}"
            )
            
            size_remote = self.sftp.stat(f"{self.remote_download_path}/{file}")
            size_local = os.stat(f"{self.local_download_path}/{file}")
            if size_remote.st_size == size_local.st_size:
                self.sftp.remove(f"{self.remote_download_path}/{file}")
                results['transfert'].append(file)
                if not EDIMSSSDocuments.objects.filter(filename=file_name).first():
                    try:
                        EDIMSSSDocuments(filename=file_name).save()
                    except Exception as e:
                        print('FUCK', e)
                        pass
            else:
                errors.append(file)

            del file_name

        EDIMSSSLogs(
            filename="",
            payload=files,
            response=[results],
            errors={'get_files': errors}
        ).save()

        return results

    def upload_files(self):
        self.connect()
        results = {'transfert':[], 'errors':[]}
        files = os.listdir(self.local_upload_path)
        for file in files:
            if file != 'process':
                size_local = os.stat(f"{self.local_upload_path}/{file}")
                self.sftp.put(
                    f"{self.local_upload_path}/{file}",
                    f"{self.remote_upload_path}/{file}"
                )
                size_remote = self.sftp.stat(f"{self.remote_upload_path}/{file}")
                if size_remote.st_size == size_local.st_size and size_remote.st_size > 0:
                    Util.check_directory(self.local_upload_process_path)
                    Util.move(f"{self.local_upload_path}/{file}", f"{self.local_upload_process_path}/{file}")
                    results['transfert'].append(file)
                else:
                    results['errors'].append(file)
        return results