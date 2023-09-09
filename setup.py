from setuptools import find_packages, setup
setup(
    name='dbh_pyutils',
    packages=find_packages(include=['dbh_pyutils']),
    version='0.1.0',
    description='DBH Utils Python library',
    author='Darren Hicks',
    license='MIT',
    install_requires=['python-dotenv', 'chromadb', 'pytube', 'numpy==1.23'],
    # setup_requires=['pytest-runner'],
    # tests_require=['pytest==4.4.1'],
    # test_suite='tests',
)