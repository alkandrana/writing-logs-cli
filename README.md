# Writing Logs CLI
```wlogs``` is a command line utility for recording writing session data (start and stop time, words written, etc.) and saving it both to a local file and to a remote API.
It also includes commands for simple analysis of the data, such as word count over a span of time (date, month, year, etc.)
Common commands are located in the "commands" directory; the "library" directory contains basic CRUD utilities customized to my [Writing Sessions API](https://github.com/alkandrana/WritingSessionsAspApi.git)

## Prerequisites

* **Python:** Version 3.10 or higher
* **Pip:** Package manager

## Installation:

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/alkandrana/writing-logs-cli.git](https://github.com/alkandrana/writing-logs-cli.git)
   cd writing-logs-cli
2. **Create and activate a virtual environment:**
```python -m venv .venv```

# On macOS/Linux:
```source venv/bin/activate```

# On Windows:
```.venv\Scripts\activate```

3. **Install dependencies:**
    ``` pip install -r requirements.txt```

## Setup:
Prior to use, the program needs to know the location of the user's local log file and the API URL. Initialise it with the following command:
```wlogs config```
The program will prompt for the name of the log file (only the name of the file is required, not the full path), and the API url.

At this point, it should be possible to run any of the program's commands, such as: ```wlogs count -d 2026-09 -c``` to view cumulative word count for the month of September.

## Command Reference
### Start a session
```wlogs session start -s <scene-code>```
### Stop session and save to API + local file:
```wlogs session stop -w <word-count>```
### Save a session retroactively (no time data):
```wlogs session save -s <scene-code> -d <date in ISO format> -w <word-count>```
### To view usage for any command: 
```wlogs [command] -h/--help```




