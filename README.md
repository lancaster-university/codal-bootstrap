# CODAL-Bootstrap

[![Bootstrap a new project from scratch](https://github.com/lancaster-university/codal-bootstrap/actions/workflows/build.yml/badge.svg?branch=main&event=push)](https://github.com/lancaster-university/codal-bootstrap/actions/workflows/build.yml)

Bootstrap a CODAL-based project from a single Python script.

An example of creating a microbit-v2 project from just one initial build file:
[![asciicast](https://asciinema.org/a/9UiUwL1klBN58UYuqDJo1IY1E.svg)](https://asciinema.org/a/9UiUwL1klBN58UYuqDJo1IY1E)

## Usage

1. Download a copy of `./build.py` ( [curl/wget/download link](https://raw.githubusercontent.com/lancaster-university/codal-bootstrap/main/build.py) ) from this repository and put in a new folder for your project
2. In the terminal/console run `./build.py` to retrieve a list of valid targets
3. Run `./build.py codal-microbit-v2` (replace `codal-microbit-v2` with your selected target)
4. Write your code in the newly created `source/` directory

Any further runs of `./build.py` will now use the latest downloaded version of the build tools, and will take the same arguments as traditional builds (see `./build.py --help` for deatils).

## Alternative Targets

Some additional targets can be included by including new URLs to `build.py`'s `TARGET_LIST` variable, by default this is as follows:

```
TARGET_LIST = [
    "https://raw.githubusercontent.com/lancaster-university/codal/master/utils/targets.json"
]
```

To add the beta-targets list, include the URL: `https://raw.githubusercontent.com/lancaster-university/codal-bootstrap/main/beta-targets.json` like so:

```
TARGET_LIST = [
    "https://raw.githubusercontent.com/lancaster-university/codal/master/utils/targets.json",
    "https://raw.githubusercontent.com/lancaster-university/codal-bootstrap/main/beta-targets.json"
]
```

## How do I reset bootstrap to run it again?

To force bootstrap mode to run again, simply remove the `codal.json` file in your project directory, and follow the installation steps above.
You may also want to remove your `libraries` folder entirely to force all libraries to be re-downloaded.
