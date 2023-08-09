import os
import hashlib
import requests
import shutil

from urllib.parse import urlparse
from cloud import *

class Cache:

    def download_file(self, url, path):
        if os.path.isfile(path):
            return
        dir = os.path.dirname(path)
        if not os.path.exists(dir):
            os.mkdir(dir)
        print(f"  downloading {url}")
        with requests.get(url, stream=True) as r:
            with open(path, 'wb') as f:
                shutil.copyfileobj(r.raw, f)

    # take URL and create a path fo a cache file

    def cache_path(self, url):
        basename = os.path.basename(url)
        md5 = hashlib.md5(url.encode('utf-8')).hexdigest()
        return os.path.join(CLOUD_IMAGES, md5, basename)

    def image(self, url):
        parts = urlparse(url)
        if parts.scheme == '':
            return url
        path = self.cache_path(url)
        self.download_file(url, path)
        return path
