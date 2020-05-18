from mtm.components.downloader import Downloader
import multiprocessing
from functools import partial


all_urls = [
    "https://www.youtube.com/watch?v=G8GWtGZuHSk",
    "https://www.youtube.com/watch?v=Vn4wxZlaFYc",
    "https://www.youtube.com/watch?v=ObO6XEQSWak",
    "https://www.youtube.com/watch?v=fPz2tZibAAQ",
    "https://www.youtube.com/watch?v=v0ADJy2Menk",
    "https://www.youtube.com/watch?v=4ugMwV6JKXE",
    "https://www.youtube.com/watch?v=J7OSA6Kw2-s",
    "https://www.youtube.com/watch?v=luRkeDCoxZ4",
    "https://www.youtube.com/watch?v=2DUWs4WO__Y",
    "https://www.youtube.com/watch?v=gmar4gh5nIw",
    "https://www.youtube.com/watch?v=aJaZc4E8Y4U",
    "https://www.youtube.com/watch?v=CU2777IVMGU",
    "https://www.youtube.com/watch?v=IvjMgVS6kng",
    "https://www.youtube.com/watch?v=DEqgTkRMYso",
    "https://www.youtube.com/watch?v=CxQByCIzZ64",
]


def download(url):
    dwl = Downloader()
    dwl.download(url, "/home/xy/repo/python/mtm/cache/youtube")


if __name__ == "__main__":
    prs = []
    batch_ = 3
    start_ = 0
    end_ = start_ + batch_
    while True:
        for url_ in all_urls[start_ : start_ + batch_]:
            pr = multiprocessing.Process(target=partial(download, url_))
            pr.start()
            prs.append(pr)
        for i, p in enumerate(prs):
            p.join()

        if start_ + batch_ == len(all_urls):
            break
        start_ += batch_
        if start_ + batch_ >= len(all_urls):
            batch_ = len(all_urls) - start_
        # for url_ in urls:
        #
        #     print("start download:%s" % url_)
        # if end_ == len(all_urls):
        #     break
        # end_ = start_ + batch_
        # if end_ > len(all_urls):
        #     end_ = len(all_urls)
  