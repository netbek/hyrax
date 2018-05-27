# Hyrax

An example of using Altair and ggplot2 in Pyramid.

## Installation

1. Install system dependencies:

    ```
    sudo apt-get install build-essential curl g++ gcc python-dev r-base
    ```

2. Install NVM and Node 8.x:

    ```
    curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.33.8/install.sh | bash
    source ~/.bashrc
    nvm install v8.9.4
    nvm alias default v8.9.4
    ```

3. Install Node, Python and R dependencies:

    ```
    cd /path/to/hyrax
    ./install.sh
    ```

## Usage

1. Start the app:

    ```
    cd /path/to/hyrax
    ./start.sh
    ```

2. Open http://localhost:8080

## License

Copyright (c) 2018 Hein Bekker. Licensed under the GNU Affero General Public License, version 3.
