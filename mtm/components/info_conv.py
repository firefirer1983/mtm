import logging
from ..utils.emoji_filter import filter_emoji

log = logging.getLogger(__file__)


extract_spec = {
    "_filename": str,
    "title": str,
    "fulltitle": str,
    "categories": list,
    "description": str,
    "duration": int,
    "id": str,
    "filesize": int,
    "uploader": str,
    "extractor": str,
    "tags": list,
}


def info_convert(info):
    ret = extract_spec.copy()
    for k, fmt in extract_spec.items():
        try:
            v = info.get(k)
        except KeyError as e:
            log.exception(e)
            log.warning("No such info key:%s in json" % k)
            ret[k] = ""
            continue

        if fmt is str:
            ret[k] = filter_emoji(v) if v else ""
        elif fmt is int:
            ret[k] = int(v) if v else 0
        elif fmt is list:
            arr = list()
            if v:
                for p in v:
                    arr.append(filter_emoji(p))
            ret[k] = arr

    return ret
