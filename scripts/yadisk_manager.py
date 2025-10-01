"""Script with DiskManager class and functions for moodle backup"""

from datetime import datetime
from os import environ, path
from logging import getLogger

import yadisk


logger = getLogger("root")


class DiskManager:
    """Light YaDisk manager"""

    def __init__(self, download_path="./"):
        self.client = yadisk.Client(token=environ.get("YADISK_TOKEN"))
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
        """dowload from remote_path to self.download_path

        Args:
            remote_path (str): full path to file on yadisk

        Returns:
            str: path to downloaded file
        """
        local_path = self.download_path + path.basename(remote_path)
        self.client.download(remote_path, local_path)
        return local_path

    def publish_file(self, remote_path: str):
        """publish file

        Args:
            remote_path (str): full path to file on yadisk

        Returns:
            str: publish link to file
        """
        self.client.publish(remote_path)
        publish_link = self.client.get_meta(remote_path).public_url
        print(f"{remote_path} link: {publish_link}")
        return publish_link


def upload_file_to_disk(
    file_path: str,
    abs_disk_path="/Учебные дисциплины - таблицы и формы",
    overwrite=True,
    publish=True,
):
    """hardcoded logic for uploading rating file to yadisk in pdf format
    might be run from bash

    Args:
        file_path (str): path to local file
        abs_disk_path (str, optional): full path to file on yadisk.
            Defaults to "/Учебные дисциплины - таблицы и формы".
        overwrite (bool): overwrite file. Defaults to true

    """
    full_path = f"{abs_disk_path}/{file_path}"
    disk_manager = DiskManager()
    disk_manager.upload(file_path, full_path, overwrite=overwrite)
    if publish:
        disk_manager.publish_file(full_path)
