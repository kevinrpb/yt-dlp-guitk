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
src_dirpath = root_dirpath / Path("dist/pyinstaller")
dst_dirpath = root_dirpath / Path("artifacts")

src_filepaths = {
    MatrixRunsOn.MACOS_14: src_dirpath / Path("macosx_14_0_arm64/yt-dlp-guitk.app"),
    MatrixRunsOn.WINDOWS_LATEST: src_dirpath / Path("win_amd64/yt-dlp-guitk.exe"),
}

platform_names = {
    MatrixRunsOn.MACOS_14: "macOS",
    MatrixRunsOn.WINDOWS_LATEST: "Windows",
}


ARCHIVE_FORMAT = "zip"


def main():
    runs_on = MatrixRunsOn(sys.argv[1])
    app_version = sys.argv[2]

    platform_name = platform_names[runs_on]

    src_filepath = src_filepaths[runs_on]
    dst_filepath = dst_dirpath / Path(f"yt-dlp-guitk_{app_version}_{platform_name}{src_filepath.suffix}")

    print(
        f"""
runs_on: {runs_on}
platform_name: {platform_name}
app_version: {app_version}
src: {src_filepath}
dst: {dst_filepath}
    """
    )

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
