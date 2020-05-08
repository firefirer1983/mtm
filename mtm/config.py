download_conf = [
    "--proxy=socks5://127.0.0.1:17720",
    "--write-thumbnail",
    "--write-info-json",
    "--ffmpeg-location=/usr/bin/ffmpeg",
    "--output=youtube/%(id)s/%(id)s.%(ext)s",
    "--format=m4a",
]

validate_conf = [
    "--proxy=socks5://127.0.0.1:17720",
    "--no-warnings",
    "--dump-json",
]
