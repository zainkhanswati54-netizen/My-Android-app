"""
Python-for-Android recipe for aiohttp
Async HTTP library — required by edge-tts
"""
from pythonforandroid.recipe import PythonRecipe


class AiohttpRecipe(PythonRecipe):
    version = '3.9.3'
    url = 'https://pypi.python.org/packages/source/a/aiohttp/aiohttp-{version}.tar.gz'

    name = 'aiohttp'

    depends = [
        'python3',
        'setuptools',
        'aiosignal',
        'frozenlist',
        'async-timeout',
        'attrs',
        'multidict',
        'yarl',
    ]

    call_hostpython_via_targetpython = False
    install_in_hostpython = False

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        # Disable C extensions for Android compatibility
        env['AIOHTTP_NO_EXTENSIONS'] = '1'
        return env


recipe = AiohttpRecipe()
