#!/usr/bin/env python
"""Backup files to iCloud Drive"""

import os
from datetime import datetime
import tempfile
import pathlib
import shutil
import click
from pyicloud import PyiCloudService
from pyicloud.services.drive import DriveNode
import dotenv


@click.command()
@click.argument("source")
@click.argument("destdir")
@click.option("--mode", type=click.Choice(["mirror", "newdir"]), default="newdir")
def backup(source, destdir, mode):
    api = _login()

    with tempfile.TemporaryDirectory() as tempdir_zip, \
            tempfile.TemporaryDirectory() as tempdir_source:
        if not os.path.isdir(source):
            shutil.copyfile(source, tempdir_source)
            source = tempdir_source

        zip_name = datetime.utcnow().strftime("%Y-%m-%d_%H.%M.%S")
        zip_path = pathlib.Path(tempdir_zip) / zip_name
        zip_path = shutil.make_archive(zip_path, "zip", source)

        # workaround for https://github.com/picklepete/pyicloud/issues/384
        # (works only after using drive API at least once)
        api.drive.root.dir()
        api._drive.params["clientId"] = api.client_id

        destdir_node = _mkdir_p(api.drive.root, "ibackup", destdir)

        # for some reason, PyIcloud can't handle uploading from parent paths
        curdir = os.curdir
        os.chdir(tempdir_zip)
        with open(os.path.basename(zip_path), "rb") as f:
            destdir_node.upload(f)
        os.chdir(curdir)


def _login() -> PyiCloudService:
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

    return api


def _mkdir_p(node: DriveNode, *components) -> DriveNode:
    for component in components:
        if component not in node.dir():
            node.mkdir(component)
            # apparently, calling dir is sometimes needed to see result
            # since we're calling it anyway, add an extra check
            if component not in node.dir():
                raise RuntimeError(f"mkdir succeeded but {component} not visible")
        node = node[component]
    return node


if __name__ == "__main__":
    backup()
