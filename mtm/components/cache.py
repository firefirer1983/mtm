import json
import os
from pathlib import Path

from ..components.splitter import get_duration
from ..config import DEFAULT_AUDIO_FMT
from ..utils.string_fmt import parse_unique_id


class Cache:
    def __init__(self, file_path, is_partial=False):
        self._file_path = str(file_path)
        
        self._extractor = os.path.basename(os.path.dirname(self._file_path))
        self._unique_id = parse_unique_id(self.dirname)
        self._is_complete = False
        self._is_partial = is_partial
    
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


class Partial(Cache):
    def __init__(self, file_path):
        super().__init__(file_path)
    
    @property
    def duration(self):
        return 15 * 60


class Partials:
    def __init__(self):
        self._partials = []
    
    def append(self, part: Partial):
        self._partials.append(part)
    
    def __iter__(self):
        return iter(self._partials)


class Material(Cache):
    def __init__(self, file_path):
        super().__init__(file_path, False)
        self._partials = []
        with open(
            self._file_path + "/" + self.unique_id + "." + "info.json", "r"
        ) as f:
            self._info = json.loads(f.read())
    
    @property
    def total_size(self):
        return self._info["filesize"]
    
    @property
    def size(self):
        return Path(self.data_file).stat().st_size
    
    @property
    def is_complete(self):
        return self.size == self.total_size or abs(get_duration(
            self.data_file) - self.duration) < 60
    
    def add_partials(self, partials):
        self._partials = partials
    
    @property
    def duration(self):
        return self._info["duration"]
    
    def list_partials(self):
        return list(self._partials)
    
    @property
    def data_file(self):
        return self._file_path + "/" + self.unique_id + "." + self.ext
    
    @property
    def ext(self):
        return DEFAULT_AUDIO_FMT
