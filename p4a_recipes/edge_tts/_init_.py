"""
Python-for-Android recipe for edge-tts
Microsoft Neural TTS — required for voice generation
"""
from pythonforandroid.recipe import PythonRecipe


class EdgeTtsRecipe(PythonRecipe):
    version = '6.1.9'
    url = 'https://pypi.python.org/packages/source/e/edge-tts/edge_tts-{version}.tar.gz'

    name = 'edge-tts'

    depends = [
        'python3',
        'setuptools',
        'aiohttp',
        'websockets',
    ]

    call_hostpython_via_targetpython = False
    install_in_hostpython = False


recipe = EdgeTtsRecipe()
