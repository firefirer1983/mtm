import os

import xlrd

from .string_fmt import filter_emoji

nickname_repo_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "cache/nicknames.xlsx")


def get_nick_names():
    workbook = xlrd.open_workbook(nickname_repo_path)
    worksheet = workbook.sheet_by_index(0)
    nicknames = set()
    for row in range(worksheet.nrows):
        nickname = str(worksheet.cell_value(row, 0))
        nickname = filter_emoji(nickname)
        if not nickname:
            break
        nicknames.add(nickname[:6])
    return list(nicknames)
