from setuptools import find_packages, setup

NAME = 'QzEmoji'
LOWERCASE = NAME.lower()

PACKAGE = find_packages(where='src')
PACKAGE += [LOWERCASE + '.data']

setup(
    name=NAME,
    version='0.1.0.dev1',
    description='Translate Qzone emoji to text',
    author='JamzumSum',
    author_email='zzzzss990315@gmail.com',
    url='https://github.com/JamzumSum/QzEmoji',
    license="MIT",
    python_requires=">=3.8",                      # for f-string and := op
    # install_requires=[],
    tests_require=['pytest'],
    packages=PACKAGE,
    package_dir={
        "": 'src',
        LOWERCASE + ".data": 'data'
    },
    include_package_data=True,
)
