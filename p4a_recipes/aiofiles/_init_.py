"""
python-for-android recipe for aiofiles
=======================================
aiofiles is a pure Python library — simple pip install recipe.

Place this file at:
  p4a_recipes/aiofiles/__init__.py
"""

from pythonforandroid.recipe import PythonRecipe


class AiofilesRecipe(PythonRecipe):
    version = '23.2.1'
    url = 'https://files.pythonhosted.org/packages/source/a/aiofiles/aiofiles-{version}.tar.gz'
    name = 'aiofiles'
    depends = ['python3']
    site_packages_name = 'aiofiles'
    call_hostpython_via_targetpython = False


recipe = AiofilesRecipe()
