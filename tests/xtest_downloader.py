from mtm.components.downloader import Downloader
import sys
from os import path

sys.path.append(path.join(path.dirname(__file__), ".."))

url = "https://www.youtube.com/watch?v=NLJcwbpkiJ0"

if __name__ == "__main__":
    dlw = Downloader()
    dlw.test_validate(url)
