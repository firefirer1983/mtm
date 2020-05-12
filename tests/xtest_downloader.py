from mtm.components.downloader import Downloader
import sys
from os import path

sys.path.append(path.join(path.dirname(__file__), ".."))

if __name__ == "__main__":
    dlw = Downloader()
    dlw.validate_url("https://www.youtube.com/watch?v=NLJcwbpkiJ0")
    dlw.download("https://www.youtube.com/watch?v=NLJcwbpkiJ0")
