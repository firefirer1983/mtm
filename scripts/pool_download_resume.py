import os
import time
from multiprocessing import Queue, Process
from queue import Empty
from urllib import error

from mtm.components.cache_manager import YoutubeCache
from mtm.components.downloader import Downloader

CACHE_REPO = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache")
YOUTUBE_CACHE_REPO = os.path.join(CACHE_REPO, "youtube")

download_urls = [
    "https://www.youtube.com/watch?v=x-m7U5lQqnQ",
    "https://www.youtube.com/watch?v=V-dDhMydYgg",
    "https://www.youtube.com/watch?v=YG7m5iI-sg4",
    "https://www.youtube.com/watch?v=cWh4pzd9Hqg",
    "https://www.youtube.com/watch?v=hBKTdeGEK-k",
]


def download(tsk_q):
    dwl = Downloader()
    try:
        while True:
            url_ = tsk_q.get(timeout=1)
            print("start downloading %s" % url_)
            try:
                dwl.download(url_, YOUTUBE_CACHE_REPO)
            except error.HTTPError as err:
                if err.code == 429:
                    print(
                        "429 happen  too much request, clear download queue and exit")
                    tsk_q.clear()
                    return
            except Exception as e:
                print("shit happen:%s" % str(e))
            else:
                print("Finished Downloading %s" % url_)
                time.sleep(30)
    except Empty as e:
        print("No more download")


if __name__ == "__main__":
    mgr = YoutubeCache()
    resume_urls = []
    download_q = Queue()
    for url in download_urls:
        download_q.put(url)
    process_num = processes = 3  # os.cpu_count()
    prs = []
    for i in range(process_num):
        pr = Process(target=download, args=(download_q,))
        pr.start()
        prs.append(pr)
    
    for pr in prs:
        pr.join()
