from setuptools import find_packages, setup
setup(
    name='dbh-pyutils',
    packages=find_packages(),
    version='0.1.3',
    description='DBH Utils Python library',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author='Darren Hicks',
    author_email="darren.hicks@gmail.com",
    license='MIT',
    install_requires=['chromadb', 'pytube', 'nltk', 'langchain'],
    python_requires='>=3.10',
    url='https://github.com/deevis/dbh-pyutils'
    # setup_requires=['pytest-runner'],
    # tests_require=['pytest==4.4.1'],
    # test_suite='tests',
)
