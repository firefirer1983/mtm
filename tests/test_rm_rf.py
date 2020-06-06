import os
from pathlib import Path


def rm_dir_safe(dir_path):
    for d in Path(dir_path).iterdir():
        if d.is_dir():
            raise RuntimeError("Not allow to delete sub directory!")
        else:
            os.remove(str(d))
    else:
        os.rmdir(str(dir_path))


if __name__ == '__main__':
    rm_dir_safe("test_rm")
