from setuptools import build_meta as _BASE
from setuptools.build_meta import _BuildMetaBackend


class _CBuildMetaBackend(_BuildMetaBackend):
    def do_cbuild(self, wheel_directory, config_settings=None,
                    metadata_directory=None):
        return self._build_with_temp_dir(['cbuild'], '.whl',
                                         wheel_directory, config_settings)


# The primary backend
_BACKEND = _CBuildMetaBackend()

get_requires_for_build_wheel = _BASE.get_requires_for_build_wheel
get_requires_for_build_sdist = _BASE.get_requires_for_build_sdist
prepare_metadata_for_build_wheel = _BASE.prepare_metadata_for_build_wheel
build_wheel = _BACKEND.do_cbuild
build_sdist = _BASE.build_sdist


# The legacy backend
__legacy__ = _BASE._BuildMetaLegacyBackend()