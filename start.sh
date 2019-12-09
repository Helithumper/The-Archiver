#!/bin/bash

docker build . -t discord-archive

docker run \
    -e DISCORD_TOKEN=REPLACE_ME \
    -v $(pwd)/archive:/code/archive \
    discord-archive
