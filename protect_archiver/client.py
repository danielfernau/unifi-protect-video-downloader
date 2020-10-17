#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Tool to download footage within a given time range from a local UniFi Protect system """

from os import path, makedirs


class ProtectClient(object):
    def __init__(
        self,
        address: str = "unifi",
        port: int = 7443,
        username: str = "ubnt",
        password: str = None,
        verify_ssl: bool = False,
        use_unsafe_cookie_jar: bool = False,
        ignore_failed_downloads: bool = False,
        download_wait: int = 0,
        use_subfolders: bool = False,
        skip_existing_files: bool = False,
        destination_path: str = "./",
        touch_files: bool = False,
        # aka read_timeout - time to wait until a socket read response happens
        download_timeout: float = 60.0,
    ):
        self.address = address
        self.port = port
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl

        self.ignore_failed_downloads = ignore_failed_downloads
        self.download_wait = download_wait
        self.download_timeout = download_timeout
        self.use_subfolders = use_subfolders
        self.skip_existing_files = skip_existing_files
        self.touch_files = touch_files

        self.destination_path = path.abspath(destination_path)

        self.files_downloaded = 0
        self.bytes_downloaded = 0
        self.files_skipped = 0
        self.max_retries = 3

        self._access_key = None
        self._api_token = None

    # TODO
