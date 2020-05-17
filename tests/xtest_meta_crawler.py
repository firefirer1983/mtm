from mtm.components.meta_crawler import MetaCrawler
from mtm.components.extraction import get_url_formatter

if __name__ == "__main__":
    meta_crawler = MetaCrawler()
    playlist = meta_crawler.retrieve_playlist(
        "https://www.youtube.com/watch?v=Fc2O3_2kax8&list=PLw02n0FEB3E3VSHjyYMcFadtQORvl1Ssj"
    )
    print(playlist)
    formatter = get_url_formatter("youtube")
    for item in playlist:
        print(formatter.get_playable_url(item))
