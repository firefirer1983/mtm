import errno
import logging
import os
import subprocess
from decimal import Decimal

import ffmpeg

from ..config import MIN_DURATION

log = logging.getLogger(__file__)


def get_duration(file_path):
    try:
        probe = ffmpeg.probe(file_path)
        audio_stream = next(
            (
                stream
                for stream in probe["streams"]
                if stream["codec_type"] == "audio"
            ),
            None,
        )
    except ffmpeg._run.Error as e:
        return Decimal(0)
    return Decimal(audio_stream["duration"])


def get_chunked_time(duration, total_duration):
    ts = 0
    chunks = list()
    while True:
        next_ = ts + duration
        next_ = total_duration if next_ >= total_duration else next_
        if next_ - ts < MIN_DURATION:
            break
        chunks.append((ts, next_))
        if next_ >= total_duration:
            break
        ts += duration
    return chunks


def _logged_popen(cmd_line, *args, **kwargs):
    log.debug("Running command: {}".format(subprocess.list2cmdline(cmd_line)))
    return subprocess.Popen(cmd_line, *args, **kwargs)


def _makedirs(path):
    """Python2-compatible version of ``os.makedirs(path, exist_ok=True)``."""
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno != errno.EEXIST or not os.path.isdir(path):
            raise


def split_audio(
    in_filename, duration, out_pattern, verbose=False,
):
    in_filename = str(in_filename)
    total_duration = get_duration(in_filename)
    durations = get_chunked_time(duration, total_duration)
    
    for i, (start_time, end_time) in enumerate(durations):
        time = end_time - start_time
        out_filename = out_pattern.format(i, i=i)
        _makedirs(os.path.dirname(out_filename))
        
        log.info(
            "{}: start={:.02f}, end={:.02f}, duration={:.02f}".format(
                out_filename, start_time, end_time, time
            )
        )
        _logged_popen(
            (
                ffmpeg.input(in_filename, ss=start_time, t=time)
                    .output(out_filename)
                    .overwrite_output()
                    .compile()
            ),
            stdout=subprocess.PIPE if not verbose else None,
            stderr=subprocess.PIPE if not verbose else None,
        ).communicate()
    return True
