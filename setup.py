from setuptools import find_packages, setup
from qzemoji import __version__

NAME = 'QzEmoji'
LOWERCASE = NAME.lower()
PACKAGE = find_packages(where='src')
PACKAGE += [LOWERCASE + '.data']

setup(
    name=NAME,
    version=__version__,
    description='Translate Qzone emoji to text',
    author='JamzumSum',
    author_email='zzzzss990315@gmail.com',
    url='https://github.com/JamzumSum/QzEmoji',
    license="MIT",
    python_requires=">=3.8",                                                           # for f-string and := op
    install_requires=["AssetsUpdater @ git+https://github.com/JamzumSum/AssetsUpdater.git"],
    tests_require=['pytest'],
    packages=PACKAGE,
    package_dir={
        "": 'src',
        LOWERCASE + ".data": 'data'
    },
    include_package_data=True,
)
