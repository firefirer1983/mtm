import os
from multiprocessing import Process, Queue
from queue import Empty

from mtm.components.downloader import Downloader

CACHE_REPO = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache")

download_urls = [
    "https://www.youtube.com/watch?v=b5K192_hilA",
    # "https://www.youtube.com/watch?v=1ZrOxeEn3Xk",
    # "https://www.youtube.com/watch?v=JAKdceOziLM",
    # "https://www.youtube.com/watch?v=r2EXpMHEtB8",
    # "https://www.youtube.com/watch?v=9JRQkrNwXKo",
    # "https://www.youtube.com/watch?v=ed3DnP2nbrw",
    # "https://www.youtube.com/watch?v=lT8lT1sjxVk",
    # "https://www.youtube.com/watch?v=j61cl69MgIM",
    # "https://www.youtube.com/watch?v=AXVTYeFDbuM",
    # "https://www.youtube.com/watch?v=usAAuGIBZTg",
    # "https://www.youtube.com/watch?v=lz6yCQBWSU8",
    # "https://www.youtube.com/watch?v=_1n5_HknzTo",
    # "https://www.youtube.com/watch?v=YkXOLiZLFho",
    # "https://www.youtube.com/watch?v=HmCm3kgyFks",
    # "https://www.youtube.com/watch?v=VhuaXzsm_O0",
    # "https://www.youtube.com/watch?v=ebnVse36UhY",
    # "https://www.youtube.com/watch?v=Jwhss4LOGE0",
    # "https://www.youtube.com/watch?v=6xpqNMfRnUc",
    # "https://www.youtube.com/watch?v=S7R_h1qRc2E",
    # "https://www.youtube.com/watch?v=aewgrdzblJk",
    # "https://www.youtube.com/watch?v=SUabnM-0We4",
    # "https://www.youtube.com/watch?v=MwA8rmwoLvE",
    # "https://www.youtube.com/watch?v=sVld3uKBMzE",
    # "https://www.youtube.com/watch?v=Eqp0d-Uoeqk",
    # "https://www.youtube.com/watch?v=HHKpPEMxNpw",
    # "https://www.youtube.com/watch?v=cWU1o-misXI",
    # "https://www.youtube.com/watch?v=T1LGw7PVHrU",
    # "https://www.youtube.com/watch?v=Yol5fROT890",
    # "https://www.youtube.com/watch?v=mApstMXkhbw",
    # "https://www.youtube.com/watch?v=h5UpkFgpkCE",
    # "https://www.youtube.com/watch?v=4ugMwV6JKXE",
    # "https://www.youtube.com/watch?v=LEixnEKdwTM",
    # "https://www.youtube.com/watch?v=lT8lT1sjxVk",
    # "https://www.youtube.com/watch?v=AXVTYeFDbuM",
    # "https://www.youtube.com/watch?v=usAAuGIBZTg",
    # "https://www.youtube.com/watch?v=lz6yCQBWSU8",
    # "https://www.youtube.com/watch?v=_1n5_HknzTo",
    # "https://www.youtube.com/watch?v=YkXOLiZLFho",
    # "https://www.youtube.com/watch?v=HmCm3kgyFks",
    # "https://www.youtube.com/watch?v=VhuaXzsm_O0",
    # "https://www.youtube.com/watch?v=ebnVse36UhY",
    # "https://www.youtube.com/watch?v=6xpqNMfRnUc",
    # "https://www.youtube.com/watch?v=S7R_h1qRc2E",
    # "https://www.youtube.com/watch?v=aewgrdzblJk",
    # "https://www.youtube.com/watch?v=SUabnM-0We4",
    # "https://www.youtube.com/watch?v=MwA8rmwoLvE",
    # "https://www.youtube.com/watch?v=Eqp0d-Uoeqk",
    # "https://www.youtube.com/watch?v=HHKpPEMxNpw",
    # "https://www.youtube.com/watch?v=mApstMXkhbw",
    # "https://www.youtube.com/watch?v=twu-3JzD-RI",
    # "https://www.youtube.com/watch?v=3ynRsI5wtDo",
    # "https://www.youtube.com/watch?v=SVqaafea7WA",
    # "https://www.youtube.com/watch?v=ghzxtpkgRX8",
    # "https://www.youtube.com/watch?v=CU2777IVMGU",
    # "https://www.youtube.com/watch?v=r2EXpMHEtB8",
    # "https://www.youtube.com/watch?v=ed3DnP2nbrw",
    # "https://www.youtube.com/watch?v=J7OSA6Kw2-s",
    # "https://www.youtube.com/watch?v=j61cl69MgIM",
    # "https://www.youtube.com/watch?v=DEqgTkRMYso",
    # "https://www.youtube.com/watch?v=AXVTYeFDbuM",
    # "https://www.youtube.com/watch?v=usAAuGIBZTg",
    # "https://www.youtube.com/watch?v=lz6yCQBWSU8",
    # "https://www.youtube.com/watch?v=_1n5_HknzTo",
    # "https://www.youtube.com/watch?v=YkXOLiZLFho",
    # "https://www.youtube.com/watch?v=HmCm3kgyFks",
    # "https://www.youtube.com/watch?v=VhuaXzsm_O0",
    # "https://www.youtube.com/watch?v=ebnVse36UhY",
    # "https://www.youtube.com/watch?v=aewgrdzblJk",
    # "https://www.youtube.com/watch?v=SUabnM-0We4",
    # "https://www.youtube.com/watch?v=sVld3uKBMzE",
    # "https://www.youtube.com/watch?v=cWU1o-misXI",
    # "https://www.youtube.com/watch?v=T1LGw7PVHrU",
    # "https://www.youtube.com/watch?v=Yol5fROT890",
    # "https://www.youtube.com/watch?v=mApstMXkhbw",
    # "https://www.youtube.com/watch?v=twu-3JzD-RI",
    # "https://www.youtube.com/watch?v=3ynRsI5wtDo",
]

download_q = Queue()
for url in download_urls:
    download_q.put(url)


def download(tsk_q):
    while not tsk_q.empty():
        try:
            url_ = tsk_q.get(timeout=1)
        except Empty as e:
            print("No more download")
            break
        else:
            dwl = Downloader()
            print("start downloading %s" % url_)
            try:
                dwl.download(url_, os.path.join(CACHE_REPO, "youtube"))
            except Exception as e:
                print("shit happen[%s] when download:%s" % (str(e), url_))
            else:
                print("Finished Downloading %s" % url_)


if __name__ == "__main__":
    process_num = processes = os.cpu_count()
    prs = []
    for i in range(process_num):
        pr = Process(target=download, args=(download_q,))
        pr.start()
        prs.append(pr)
    
    for pr in prs:
        pr.join()
