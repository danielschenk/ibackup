#!/usr/bin/env python
"""Backup files to iCloud Drive"""

import os
import click
from pyicloud import PyiCloudService
from pyicloud.services.drive import DriveNode
import dotenv


@click.command()
@click.argument("source")
@click.argument("destdir")
@click.option("--mode", type=click.Choice(["mirror", "newdir"]), default="newdir")
def backup(source, destdir, mode):
    dotenv.load_dotenv()
    try:
        api = PyiCloudService(os.environ["ICLOUD_USERNAME"],
                              os.environ["ICLOUD_PASSWORD"],
                              cookie_directory=os.path.join(os.path.expanduser("~"),
                                                            ".python-ibackup"))
    except KeyError as e:
        raise click.UsageError(f"{e.args[0]} required but not set")

    # from pyicloud example. TODO: extend with non-interactive solution for inside Docker
    if api.requires_2fa:
        print("Two-factor authentication required.")
        code = input("Enter the code you received of one of your approved devices: ")
        result = api.validate_2fa_code(code)
        print("Code validation result: %s" % result)

        if not result:
            raise RuntimeError("Failed to verify security code")

        if not api.is_trusted_session:
            print("Session is not trusted. Requesting trust...")
            result = api.trust_session()
            print("Session trust result %s" % result)

            if not result:
                print("Failed to request trust. You will likely be prompted for the code again in the coming weeks")

    # workaround for https://github.com/picklepete/pyicloud/issues/384
    # (works only after using drive API at least once)
    api.drive.root.dir()
    api._drive.params["clientId"] = api.client_id

    _mkdir_p(api.drive.root, "ibackup", destdir)

    with open(source, "rb") as f:
        api.drive["ibackup"][destdir].upload(f)


def _mkdir_p(node: DriveNode, *components):
    for component in components:
        if component not in node.dir():
            node.mkdir(component)
            # apparently, calling dir is sometimes needed to see result
            # since we're calling it anyway, add an extra check
            if component not in node.dir():
                raise RuntimeError(f"mkdir succeeded but {component} not visible")
        node = node[component]


if __name__ == "__main__":
    backup()
