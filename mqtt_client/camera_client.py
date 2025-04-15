import requests
from requests.auth import HTTPBasicAuth
from io import BytesIO
from PIL import Image
from urllib.parse import urlparse

class IPCameraClient:
    """
    Simple client to consume an IP camera snapshot or MJPEG stream.

    Usage:
        camera = IPCameraClient(
            url='http://CAMERA_IP:PORT/snapshot.jpg',
            username='user',
            password='pass'
        )
        image = camera.get_snapshot()
        image.show()  # PIL Image

        # Or get raw bytes
        img_bytes = camera.get_snapshot_bytes()
    """
    def __init__(self, url, username=None, password=None, timeout=5):
        # Validate URL
        parsed = urlparse(url)
        if not parsed.scheme.startswith('http'):
            raise ValueError('Camera URL must start with http or https')
        self.url = url
        self.username = username
        self.password = password
        self.timeout = timeout

    def get_snapshot_bytes(self):
        """Fetch the latest snapshot as bytes."""
        auth = None
        if self.username and self.password:
            auth = HTTPBasicAuth(self.username, self.password)
        resp = requests.get(self.url, auth=auth, timeout=self.timeout, stream=True)
        resp.raise_for_status()
        return resp.content

    def get_snapshot(self):
        """Fetch the latest snapshot as a PIL Image."""
        img_bytes = self.get_snapshot_bytes()
        return Image.open(BytesIO(img_bytes)).convert('RGB')

    # Optionally, you could add MJPEG streaming support here
    # def stream_mjpeg(self):
    #     pass  # Advanced: implement frame generator for MJPEG
