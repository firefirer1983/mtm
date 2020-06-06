import os

from mtm.components.cache_manager import YoutubeCache
from mtm.config import MAX_DURATION
from mtm.model.database import scoped_session
from mtm.model.models import StorageEntry

CACHE_REPO = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache")
YOUTUBE_CACHE_REPO = os.path.join(CACHE_REPO, "youtube")


def main():
    mgr = YoutubeCache()
    uploads = []
    for cache in mgr.list_cache():
        if cache.is_complete or cache.left_over < MAX_DURATION:
            # print("%s completed! total:%u left_over:%u" % (
            #     cache.data_file, cache.duration, cache.left_over))
            partials = cache.list_partials()
            if partials:
                for partial in cache.list_partials():
                    # print("upload => %s " % partial.file_path)
                    uploads.append(partial)
            else:
                origin = cache.get_origin()
                # print("upload => %s" % origin.file_path)
                uploads.append(origin)
    for upload in uploads:
        with scoped_session(auto_commit=True) as s:
            entry = StorageEntry(
                unique_id=upload.unique_id,
                directory=os.path.dirname(upload.file_path),
                file_name=os.path.basename(upload.file_path),
                file_ext=upload.ext,
            
            )
            s.add(entry)
            print(entry)


if __name__ == "__main__":
    main()
