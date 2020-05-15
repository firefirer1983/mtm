import abc
import re
from urllib.parse import urlparse, parse_qsl


def fmt_dirname(s):

    return re.sub(
        "[’!\"#$%&'()*+,-./:;<=>?@，。?★、…【】《》？“”‘’！[\\]^_`{|}~]+", "", s,
    )


def filter_emoji(desstr, restr=""):
    # 过滤表情
    try:
        co = re.compile(u"[\U00010000-\U0010ffff]")
    except re.error:
        co = re.compile(u"[\uD800-\uDBFF][\uDC00-\uDFFF]")
    return co.sub(restr, desstr)


def remove_ext(filename):
    pos = -1
    for i, c in enumerate(reversed(filename)):
        if c is ".":
            break
        pos -= 1
    return filename[:pos]


class ParserStrategy:
    @abc.abstractmethod
    def parse(self, *args, **kwargs):
        raise NotImplementedError


class YoutubeUrlParser(ParserStrategy):
    def parse(self, data):
        for qs in parse_qsl(data.query):
            if qs[0] == "v":
                return qs[1]
        return None


class YoutubeDirnameParser(ParserStrategy):
    def parse(self, data):
        pos = -1
        for c in reversed(data):
            if c == "-":
                break
            pos -= 1
        else:
            return None
        return data[pos + 1 :]

    @property
    def extractor(self):
        return "youtube"


extractor_registry = {
    "www.youtube.com": "youtube",
}

url_parser_registry = {
    "youtube": YoutubeUrlParser(),
}


def parse_basic_info(url):
    result = urlparse(url)
    for k, v in extractor_registry.items():
        if result.netloc == k:
            parser = url_parser_registry[v]
            return v, parser.parse(url)
    else:
        raise NotImplemented("Invalid URL or not support URL")


def parse_unique_id_from_dirname(extractor, dirname):
    parser = None
    for k, v in path_parser_registry.items():
        if v.extractor == extractor:
            parser = v
    if parser:
        return parser.parse(dirname)
