"""
python-for-android recipe for edge-tts
=======================================
edge-tts is a pure Python library (no C extensions) so this
recipe is straightforward — we just install it via pip.

Place this file at:
  p4a_recipes/edge_tts/__init__.py

Then in buildozer.spec uncomment:
  p4a.local_recipes = %(source.dir)s/p4a_recipes
"""

from pythonforandroid.recipe import PythonRecipe


class EdgeTTSRecipe(PythonRecipe):
    version = '6.1.9'
    url = 'https://files.pythonhosted.org/packages/source/e/edge-tts/edge-tts-{version}.tar.gz'
    name = 'edge_tts'
    depends = ['python3', 'aiohttp', 'aiofiles']
    site_packages_name = 'edge_tts'
    call_hostpython_via_targetpython = False

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        return env


recipe = EdgeTTSRecipe()
