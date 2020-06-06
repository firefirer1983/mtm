import os
from dataclasses import dataclass
from multiprocessing import Queue, Process
from queue import Empty

from mtm.components.cache_manager import YoutubeCache
from mtm.components.splitter import split_audio
from mtm.config import MAX_DURATION

CACHE_REPO = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache")
YOUTUBE_CACHE_REPO = os.path.join(CACHE_REPO, "youtube")

split_dirs = []


@dataclass
class SplitEntry:
    path: str
    unique_id: str
    
    def __init__(self, path, unique_id):
        self.path = path
        self.unique_id = unique_id
    
    def __str__(self):
        return "SplitEntry(%s, %s)" % (self.path, self.unique_id)


def split(tsk_q):
    try:
        while True:
            info: SplitEntry = tsk_q.get(timeout=1)
            print("start splitting %s" % info.path)
            split_template = info.path + "/" \
                             + info.unique_id + ".part.{:04d}" + "." + "m4a"
            input_file = info.path + "/" + info.unique_id + ".m4a"
            try:
                split_audio(input_file, MAX_DURATION, split_template)
            except Exception as e:
                print("shit happen[%s] when split:%s" % (str(e), info.path))
            else:
                print("Finished splitting %s" % info.path)
    except Empty as e:
        print("No more to split")


if __name__ == "__main__":
    mgr = YoutubeCache()
    split_q = Queue()
    for cache in mgr.list_cache():
        if not cache.is_complete:
            print("[NOT COMPLETE] %s total duration:%u vs left over:%u" % (
                cache.file_path, cache.duration, cache.left_over))
        else:
            print("[COMPLETE] %s: duration:%u with parts:%u" % (
                cache.file_path, cache.duration, len(cache.list_partials())))
            if len(cache.list_partials()) == 0 and cache.duration > MAX_DURATION:
                split_q.put(SplitEntry(cache.file_path, cache.unique_id))
    # while True:
    #     try:
    #         entry = split_q.get(timeout=1)
    #     except Empty:
    #         break
    #     else:
    #         print(entry)
    # split_q.put(
    #     SplitEntry(
    #         "/home/xy/misc/mtm/cache/youtube/音樂治療 —— 抒情鋼琴音樂-WPJGBmDB3Yc",
    #         "WPJGBmDB3Yc"))
    process_num = 5  # os.cpu_count()
    prs = []
    for i in range(process_num):
        pr = Process(target=split, args=(split_q,))
        pr.start()
        prs.append(pr)

    for pr in prs:
        pr.join()
