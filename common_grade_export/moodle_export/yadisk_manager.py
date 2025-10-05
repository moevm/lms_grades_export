"""Script with DiskManager class and functions for moodle backup

"""
from datetime import datetime
from os import environ, path
from logging import getLogger

import yadisk


logger = getLogger()


class DiskManager():
    """Light YaDisk manager
    """

    def __init__(self, yatoken=None, download_path='./'):
        self.client = yadisk.Client(token=yatoken or environ.get('YADISK_TOKEN'))
        self.download_path = download_path

    def upload(self, local_path: str, disk_path: str, overwrite=True):
        """upload from local_path to disk_path

        Args:
            local_path (str): path to local file 
            disk_path (str): full path to file on yadisk
            overwrite (bool): overwrite file. Defaults to true
        """
        logger.info("Uploading %s to %s", *(local_path, disk_path))
        self.client.upload(local_path, disk_path, overwrite=overwrite)

    def download_file_from_disk(self, remote_path: str):
        """_summary_

        Args:
            remote_path (str): full path to file on yadisk

        Returns:
            str: path to downloaded file 
        """
        local_path = self.download_path + path.basename(remote_path)
        self.client.download(remote_path, local_path)
        return local_path
