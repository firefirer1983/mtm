import json
import os
from pathlib import Path

from ..components.splitter import get_duration
from ..config import DEFAULT_AUDIO_FMT, MAX_DURATION, MIN_DURATION
from ..utils.string_fmt import is_partial_file


class Cache:
    def __init__(self, file_path, is_partial=False):
        self._file_path = str(file_path)
        
        self._extractor = os.path.basename(os.path.dirname(self._file_path))
        if len(self.dirname) == 11:
            self._unique_id = self.dirname
        else:
            raise RuntimeError("dirname not a vid")
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
    
    @property
    def ext(self):
        return DEFAULT_AUDIO_FMT


class Partial(Cache):
    def __init__(self, file_path, unique_id):
        self._unique_id = unique_id
        self._file_path = str(file_path)
        self._is_partial = True
    
    @property
    def duration(self):
        return 15 * 60


class Origin(Cache):
    def __init__(self, file_path, unique_id):
        self._unique_id = unique_id
        self._file_path = str(file_path)
        self._is_partial = False
    
    @property
    def duration(self):
        return get_duration(self._file_path)


class Material(Cache):
    def __init__(self, file_path):
        super().__init__(file_path, False)
        self._origin = Origin(self.data_file, self.unique_id)
        self._partials = []
        with open(
            self._file_path + "/" + self.unique_id + "." + "info.json", "r"
        ) as f:
            self._info = json.loads(f.read())
        
        for d in Path(self._file_path).iterdir():
            if is_partial_file(d):
                self._partials.append(Partial(d, self.unique_id))
        self._partials = sorted(self._partials, key=lambda x: x.file_path)
        self._left_over = 0
    
    @property
    def total_size(self):
        return self._info["filesize"]
    
    @property
    def size(self):
        try:
            return Path(self.data_file).stat().st_size
        except FileNotFoundError as e:
            return 0
    
    @property
    def is_complete(self):
        self._left_over = abs(self.get_origin().duration - self.duration)
        return self.size == self.total_size or self._left_over < 60
    
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
        return self._file_path + "/" + self.unique_id + "." + self.ext
    
    @classmethod
    def create(cls, path):
        return Material(path)
    
    @property
    def is_split(self):
        part_num = len(self._partials)
        if abs(self._origin.duration - part_num * MAX_DURATION) < MIN_DURATION:
            return True
    
    def get_origin(self) -> Origin:
        return self._origin
    
    def refresh_cache(self):
        self._origin = Origin(self.data_file, self.unique_id)
        self._partials = []
        for d in Path(self._file_path).iterdir():
            if is_partial_file(d):
                self._partials.append(Partial(d, self.unique_id))
