# import os
# from pathlib import Path
#
# cache_path = "/home/xy/misc/mtm/cache/youtube"
#
#
# def main():
#     for dirname in Path(cache_path).iterdir():
#         print(str(dirname)[-11:])
#         vid = str(dirname)[-11:]
#         print("rename %s -> %s" % (
#             str(dirname), os.path.join(os.path.dirname(str(dirname)), vid)
#         ))
#         os.rename(str(dirname), os.path.join(os.path.dirname(str(dirname)), vid))
#
#
# if __name__ == '__main__':
#     main()
