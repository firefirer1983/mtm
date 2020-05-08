from mtm.crawler import Crawler


if __name__ == "__main__":
    cwl = Crawler()
    print(cwl.validate_url("https://www.youtube.com/watch?v=PJ1QwhNL72A"))
