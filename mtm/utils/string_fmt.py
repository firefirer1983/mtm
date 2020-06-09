import re

RE_IS_PARTIAL = re.compile("\.part\.[0-9]{4}.m4a$")
RE_IS_MATERIAL = re.compile("^[\S\s]*-(.*)$")
RE_PARTIAL_UNIQUE_ID = re.compile("-(.*)(?:\.part\.[0-9]{4}).m4a$")
RE_UNCUT_UNIQUE_ID = re.compile("-(.*)$")
RE_EXTENSION = re.compile("^.*\.(.*)$")


def fmt_dirname(s):
    return re.sub(
        "[’!\"#$%&'()*+,-./:;<=>?@，。?★、…【】《》？“”‘’！[\\]^_`{|}~]+", "", s
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


def is_partial_file(dir_name):
    res = RE_IS_PARTIAL.search(str(dir_name))
    return bool(res)


def parse_unique_id(dir_name):
    dir_name = str(dir_name)
    res = RE_UNCUT_UNIQUE_ID.search(dir_name)
    return res.groups()[0] if len(res.groups()) else None


def check_file_with_ext(ext, file_path):
    re_ext_file = re.compile(".%s$" % ext)
    return bool(re_ext_file.search(str(file_path)))


def is_material_dir(dir_name):
    return bool(RE_IS_MATERIAL.search(str(dir_name)))


def is_playlist(url):
    pass


def parse_ext(file_name):
    res = RE_EXTENSION.search(file_name)
    if not len(res.groups()):
        raise RuntimeError("No extension found!")
    return res.groups()[0]
