import os
from os.path import dirname
from pathlib import Path


__file__ = "/home/xy/repo/python/mtm/mtm/components/cache_manager.py"
cache_dir_name = "cache"
default_cache_root = dirname(dirname(dirname(__file__))) + "/" + cache_dir_name

for path in Path(default_cache_root).iterdir():
    for video_dir in path.iterdir():
        print(video_dir)
