from mtm.components.downloader import Downloader


if __name__ == "__main__":
    dwl = Downloader()
    print(dwl.validate_url("https://www.youtube.com/watch?v=PJ1QwhNL72A"))
