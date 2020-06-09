import json
import os
from pathlib import Path

from ..components.splitter import get_duration
from ..config import DEFAULT_AUDIO_FMT, MAX_DURATION, MIN_DURATION
from ..utils.string_fmt import is_partial_file, filter_emoji


class Cache:
    def __init__(self, file_path, unique_id, title, is_partial=False):
        self._file_path = str(file_path)
        self._is_complete = False
        self._unique_id = unique_id
        self._title = title
        self._is_partial = is_partial
        self._duration = None
    
    @property
    def unique_id(self):
        return self._unique_id
    
    @property
    def parent_dir(self):
        return os.path.dirname(self._file_path)
    
    @property
    def file_path(self):
        return self._file_path
    
    @property
    def dirname(self):
        return os.path.basename(self._file_path)
    
    @property
    def is_partial(self):
        return self._is_partial
    
    @property
    def ext(self):
        return DEFAULT_AUDIO_FMT
    
    @property
    def duration(self):
        if self._duration is None:
            self._duration = get_duration(self._file_path)
        return self._duration
    
    @property
    def size(self):
        try:
            return Path(self.file_path).stat().st_size
        except FileNotFoundError as e:
            return 0
    
    @property
    def title(self):
        return self._title


class Partial(Cache):
    def __init__(self, file_path, unique_id, title):
        self._unique_id = unique_id
        super().__init__(file_path, unique_id, title, is_partial=True)
    

class Origin(Cache):
    def __init__(self, file_path, unique_id, title):
        self._unique_id = unique_id
        super().__init__(file_path, unique_id, title, is_partial=False)


class Material:
    def __init__(self, file_path):
        self._file_path = str(file_path)
        self._partials = []
        self._extractor = os.path.basename(os.path.dirname(self._file_path))
        self._dirname = os.path.basename(self._file_path)
        self._unique_id = self._dirname
        assert len(self._unique_id) == 11, "Invalid vid:%s" % self._unique_id
        with open(
            self._file_path + "/" + self._unique_id + "." + "info.json", "r"
        ) as f:
            self._info = json.loads(f.read())
        origin_title = filter_emoji(self._info["title"])[:256]
        partials = []
        for d in Path(self._file_path).iterdir():
            if is_partial_file(d):
                partials.append([d, self._unique_id])
        partials = sorted(partials, key=lambda x: x[0])
        for index, p in enumerate(partials):
            self._partials.append(
                Partial(p[0], p[1], origin_title + " PART %u" % index))
        self._left_over = 0
        
        self._origin = Origin(self._file_path + "/" + self._unique_id + ".m4a",
                              self._unique_id, origin_title)
    
    @property
    def total_size(self):
        return self._info["filesize"]
    
    @property
    def is_complete(self):
        self._left_over = abs(self.get_origin().duration - self.duration)
        return self.get_origin().size == self.total_size or self._left_over < 60
    
    @property
    def left_over(self):
        if self.is_complete:
            return 0
        return self._left_over
    
    @property
    def duration(self):
        return self._info["duration"]
    
    def list_partials(self):
        return self._partials
    
    @property
    def data_file(self):
        return self.get_origin().file_path
    
    @classmethod
    def create(cls, path):
        return Material(path)
    
    @property
    def is_split(self):
        part_num = len(self._partials)
        if abs(
            self.get_origin().duration - part_num * MAX_DURATION) < MIN_DURATION:
            return True
    
    def get_origin(self) -> Origin:
        return self._origin
    
    def refresh_cache(self):
        self._origin = Origin(self.data_file, self._unique_id)
        self._partials = []
        for d in Path(self._file_path).iterdir():
            if is_partial_file(d):
                self._partials.append(Partial(d, self._unique_id))
    
    def unique_id(self):
        return self.get_origin().unique_id
