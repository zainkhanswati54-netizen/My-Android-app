"""
Python-for-Android recipe for edge-tts
Microsoft Edge Neural TTS — free, real voices, gender/speed/pitch support
"""
from pythonforandroid.recipe import PythonRecipe


class EdgeTTSRecipe(PythonRecipe):
    # Latest stable version
    version = '6.1.9'
    url = 'https://pypi.python.org/packages/source/e/edge-tts/edge-tts-{version}.tar.gz'

    name = 'edge-tts'

    # edge-tts depends on aiohttp for async HTTP streaming
    depends = ['python3', 'aiohttp']

    # Pure Python package — no C compilation needed
    call_hostpython_via_targetpython = False
    install_in_hostpython = False

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        return env


recipe = EdgeTTSRecipe()
