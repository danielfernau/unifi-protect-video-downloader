from .download import *  # NOQA


def main():
    import logging
    import os
    import urllib3

    logging.basicConfig(format="%(message)s", level=logging.INFO)

    os.environ.setdefault("PYTHONUNBUFFERED", "true")

    # disable InsecureRequestWarning for unverified HTTPS requests
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    from .base import cli

    cli.main()
