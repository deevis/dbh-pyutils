# DBH PyUtils

These are Python utilities I'm building out as I traverse the machine learning landscape

## Prerequisites

You'll want to have Python > 3.10 installed

And pip (you gotta have pip intalled ffs)


## To build/install locally

```
cd myprojects
git clone https://github.com/deevis/dbh-pyutils.git
cd dbh-pyutils
python setup.py bdist_wheel
pip install --force-reinstall .\dist\dbh_pyutils-0.1.0-py3-none-any.whl
```


## Usage

### searchYouTubeAPI and getYouTubeVideoInfo
Require YOUTUBE_API_KEY be set for os.getenv('YOUTUBE_API_KEY') to succeed

### Branches

* main

