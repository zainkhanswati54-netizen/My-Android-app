from setuptools import setup, find_packages

setup(
    name='titan-ai-studio-pro',
    version='5.3.0',
    description='Titan AI Studio Pro - Professional Text-to-Speech Application',
    long_description='''
    Titan AI Studio Pro is a professional text-to-speech application with support for multiple languages,
    voice types, and advanced features like file import, custom storage location, and download history.
    ''',
    long_description_content_type='text/markdown',
    author='Titan AI Team',
    author_email='support@titanai.com',
    url='https://github.com/yourusername/titan-ai-studio-pro',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'kivy>=2.2.1',
        'gTTS>=2.3.2',
        'requests>=2.31.0',
        'pillow>=10.1.0',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Topic :: Multimedia :: Sound/Audio :: Speech',
    ],
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'titan-ai=main:main',
        ],
    },
)
