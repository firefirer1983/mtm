import abc
import logging
import os
from pathlib import Path

from mtm.components.cache import Material
from ..utils.dir_tools import rm_dir_safe
from ..utils.string_fmt import is_material_dir, is_partial_file

log = logging.getLogger(__file__)

CACHE_REPO = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "cache")


class CacheManager(abc.ABC):
    def __init__(self, name):
        self._extractor = name
    
    @property
    def dirname(self):
        return str(self._extractor)
    
    @abc.abstractmethod
    def get_cache(self, unique_id):
        pass
    
    @property
    def repo_path(self):
        return os.path.join(CACHE_REPO, self.dirname)


class YoutubeCache(CacheManager):
    def __init__(self, name):
        super().__init__(name=name)
        self._materials = {}
        
        for d in Path(self.repo_path).iterdir():
            if not is_partial_file(str(d)):
                material = Material.create(d)
                self._materials[material.unique_id] = material
                
    def get_cache(self, unique_id):
        return self._materials.get(unique_id, None)
    
    def list_cache(self):
        return self._materials.values()
    
    def purge_cache_partials(self, unique_id):
        material = self._materials.get(unique_id, None)
        if material:
            for partial in material.list_partials():
                rm_dir_safe(partial.file_path)
            material.refresh_partials()
    
    def purge_cache_only(self, unique_id):
        material = self._materials[unique_id]
        if material:
            self.purge_cache_partials(unique_id)
            rm_dir_safe(material.file_path)
            del self._materials[unique_id]
            return True

    def purge_cache_and_partials(self, unique_id):
        material = self._materials[unique_id]
        self.purge_cache_partials(unique_id)
        rm_dir_safe(material.file_path)
        del self._materials[unique_id]
        return True

