#!/usr/bin/env python3

import os
import shutil
import sys
from enum import Enum
from pathlib import Path


class MatrixRunsOn(Enum):
    WINDOWS_LATEST = "windows-latest"


root_dirpath = Path(__file__).parent.parent.resolve()
src_dirpath = root_dirpath / Path("dist/pyinstaller")
dst_dirpath = root_dirpath / Path("artifacts")

src_filepaths = {MatrixRunsOn.WINDOWS_LATEST: src_dirpath / Path("win_amd64/yt-dlp-guitk.exe")}


def main():
    runs_on = MatrixRunsOn(sys.argv[1])
    app_version = sys.argv[2]

    src_filepath = src_filepaths[runs_on]
    dst_filepath = dst_dirpath / Path(f"yt-dlp-guitk_{app_version}_{runs_on.value}{src_filepath.suffix}")

    print(
        f"""
runs_on: {runs_on}
app_version: {app_version}
src: {src_filepath}
dst: {dst_filepath}
    """
    )

    os.makedirs(dst_dirpath, exist_ok=True)
    shutil.copy(src_filepath, dst_filepath)


if __name__ == "__main__":
    main()
