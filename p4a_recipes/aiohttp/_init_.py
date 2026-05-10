"""
python-for-android recipe for aiohttp
======================================
aiohttp has C extensions (speedups) but works fine without them.
We build it with --no-build-isolation to avoid compilation issues on Android.

Place this file at:
  p4a_recipes/aiohttp/__init__.py
"""

from pythonforandroid.recipe import PythonRecipe


class AiohttpRecipe(PythonRecipe):
    version = '3.9.3'
    url = 'https://files.pythonhosted.org/packages/source/a/aiohttp/aiohttp-{version}.tar.gz'
    name = 'aiohttp'
    depends = ['python3', 'multidict', 'yarl', 'frozenlist', 'async_timeout', 'attrs']
    site_packages_name = 'aiohttp'
    call_hostpython_via_targetpython = False

    # Disable C extension speedups — pure Python fallback is fine for Android
    def build_arch(self, arch):
        env = self.get_recipe_env(arch)
        env['AIOHTTP_NO_EXTENSIONS'] = '1'
        super().build_arch(arch)

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        env['AIOHTTP_NO_EXTENSIONS'] = '1'
        return env


recipe = AiohttpRecipe()
