#!/usr/bin/env python3

import errno
import os
import shutil
import sys
from enum import Enum
from pathlib import Path


class MatrixRunsOn(Enum):
    WINDOWS_LATEST = "windows-latest"
    MACOS_14 = "macos-14"


root_dirpath = Path(__file__).parent.parent.resolve()
src_dirpath = root_dirpath / Path("dist")
dst_dirpath = root_dirpath / Path("artifacts")

src_filepaths = {
    MatrixRunsOn.MACOS_14: src_dirpath / Path("yt-dlp-guitk.zip"),
    MatrixRunsOn.WINDOWS_LATEST: src_dirpath / Path("yt-dlp-guitk.exe"),
}

platform_names = {
    MatrixRunsOn.MACOS_14: "macOS",
    MatrixRunsOn.WINDOWS_LATEST: "Windows",
}

needs_zip = [MatrixRunsOn.WINDOWS_LATEST]


def main():
    runs_on = MatrixRunsOn(sys.argv[1])
    app_version = sys.argv[2]

    platform_name = platform_names[runs_on]

    src_filepath = src_filepaths[runs_on]
    dst_filepath = dst_dirpath / Path(f"yt-dlp-guitk_{app_version}_{platform_name}{src_filepath.suffix}")

    do_zip = runs_on in needs_zip

    print(
        f"""
runs_on: {runs_on}
platform_name: {platform_name}
app_version: {app_version}
src: {src_filepath}
dst: {dst_filepath}
do_zip: {do_zip}
    """
    )

    # Check if we need to zip it first
    if do_zip:
        zip_filepath = src_dirpath / "tmp"

        shutil.make_archive(zip_filepath, "zip", src_filepath.parent, src_filepath.name)

        # Set src_filepath as the zip
        src_filepath = f"{zip_filepath}.zip"

    os.makedirs(dst_dirpath, exist_ok=True)

    try:
        shutil.copytree(src_filepath, dst_filepath)
    except OSError as e:
        if e.errno in (errno.ENOTDIR, errno.EINVAL):
            shutil.copy(src_filepath, dst_filepath)
        else:
            raise e


if __name__ == "__main__":
    main()
