# AoikCherryPyStudy
Python **CherryPy** library study.

Tested working with:
- Python 2.7 and 3.5
- CherryPy 8.1.2

Trace call using [AoikTraceCall](https://github.com/AoiKuiyuyou/AoikTraceCall):
- [RequestHandlerCPWSGIServerTraceCall.py](/src/RequestHandlerCPWSGIServerTraceCall.py)
- [RequestHandlerCPWSGIServerTraceCallLogPy2.txt](/src/RequestHandlerCPWSGIServerTraceCallLogPy2.txt?raw=True)
- [RequestHandlerCPWSGIServerTraceCallLogPy2Thread0.txt](/src/RequestHandlerCPWSGIServerTraceCallLogPy2Thread0.txt?raw=True)
- [RequestHandlerCPWSGIServerTraceCallLogPy2Thread1.txt](/src/RequestHandlerCPWSGIServerTraceCallLogPy2Thread1.txt?raw=True)
- [RequestHandlerCPWSGIServerTraceCallLogPy2Thread2.txt](/src/RequestHandlerCPWSGIServerTraceCallLogPy2Thread2.txt?raw=True)
- [RequestHandlerCPWSGIServerTraceCallLogPy2Thread3.txt](/src/RequestHandlerCPWSGIServerTraceCallLogPy2Thread3.txt?raw=True)
- [RequestHandlerCPWSGIServerTraceCallLogPy3.txt](/src/RequestHandlerCPWSGIServerTraceCallLogPy3.txt?raw=True)
- [RequestHandlerCPWSGIServerTraceCallLogPy3Thread0.txt](/src/RequestHandlerCPWSGIServerTraceCallLogPy3Thread0.txt?raw=True)
- [RequestHandlerCPWSGIServerTraceCallLogPy3Thread1.txt](/src/RequestHandlerCPWSGIServerTraceCallLogPy3Thread1.txt?raw=True)
- [RequestHandlerCPWSGIServerTraceCallLogPy3Thread2.txt](/src/RequestHandlerCPWSGIServerTraceCallLogPy3Thread2.txt?raw=True)
- [RequestHandlerCPWSGIServerTraceCallLogPy3Thread3.txt](/src/RequestHandlerCPWSGIServerTraceCallLogPy3Thread3.txt?raw=True)
- [RequestHandlerCPWSGIServerTraceCallNotesPy2.txt](/src/RequestHandlerCPWSGIServerTraceCallNotesPy2.txt?raw=True)
- [RequestHandlerCPWSGIServerTraceCallNotesPy3.txt](/src/RequestHandlerCPWSGIServerTraceCallNotesPy3.txt?raw=True)

## Table of Contents
- [Set up AoikTraceCall](#set-up-aoiktracecall)
  - [Setup via pip](#setup-via-pip)
  - [Setup via git](#setup-via-git)
- [Usage](#usage)
  - [Start server](#start-server)
  - [Send request](#send-request)

## Set up AoikTraceCall
- [Setup via pip](#setup-via-pip)
- [Setup via git](#setup-via-git)

### Setup via pip
Run:
```
pip install git+https://github.com/AoiKuiyuyou/AoikTraceCall
```

### Setup via git
Run:
```
git clone https://github.com/AoiKuiyuyou/AoikTraceCall

cd AoikTraceCall

python setup.py install
```

## Usage
- [Start server](#start-server)
- [Send request](#send-request)

### Start server
Run:
```
python "AoikCherryPyStudy/src/RequestHandlerCPWSGIServerTraceCall.py" > Log.txt 2>&1
```

### Send request
Run:
```
curl -X POST -d hello http://127.0.0.1:8000/
```
