#!/bin/bash

# Build image if not exists
if [[ $(docker image inspect vvvvid-downloader:latest 2> /dev/null) == "[]" ]]; then
    docker build -t vvvvid-downloader .
fi

# Execute vvvvid-downloader
docker run -it --rm -v $(pwd)/downloads:/app/Downloads -v $(pwd)/downloads_list.txt:/app/downloads_list.txt vvvvid-downloader
