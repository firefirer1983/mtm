import abc
from urllib.parse import parse_qsl, urlparse


class ExtractionStrategy:
    def __init__(self, url):
        self._url = url
        self._extractor = None
        self._is_playlist = False
        self._unique_id = self.parse_unique_id()
        netloc = urlparse(url).netloc
        for k, v in extractor_registry.items():
            if k == netloc:
                self._extractor = v
                break
        else:
            raise NotImplemented("")

    @property
    def extractor(self):
        return self._extractor

    @property
    def is_playlist(self):
        return self._is_playlist

    @property
    def url(self):
        return self._url

    @property
    def unique_id(self):
        return self._unique_id

    @abc.abstractmethod
    def parse_unique_id(self):
        pass


class YoutubeExtraction(ExtractionStrategy):
    def __init__(self, url):
        super().__init__(url)

    def parse_unique_id(self):
        res = urlparse(self._url)
        for qs in parse_qsl(res.query):
            if qs[0] == "list":
                self._is_playlist = True
                self._unique_id = qs[1]
                break
            elif qs[0] == "v":
                self._unique_id = qs[1]
        return self._unique_id


extractor_registry = {"www.youtube.com": "youtube"}
extraction_registry = {"youtube": YoutubeExtraction}


def get_extraction(url) -> "ExtractionStrategy":
    result = urlparse(url)
    for k, v in extractor_registry.items():
        if result.netloc == k:
            cls_ = extraction_registry[v]
            extraction = cls_(url)
            return extraction
    else:
        raise NotImplemented("Invalid URL or not support URL")


class UrlFormat:
    def __init__(self, extractor):
        self._extractor = extractor

    @property
    def extractor(self):
        return self._extractor

    @abc.abstractmethod
    def get_playable_url(self, unique_id):
        pass


class YoutubeUrl(UrlFormat):
    def __init__(self):
        super().__init__("youtube")

    def get_playable_url(self, unique_id):
        return "https://www.youtube.com/watch?v=%s" % unique_id


url_fmt_registry = {"youtube": YoutubeUrl()}


def get_url_formatter(extractor):
    return url_fmt_registry[extractor]
