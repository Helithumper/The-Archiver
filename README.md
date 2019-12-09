# The Archiver

This is a bot created to archive old Discord channels. Discord does not have any native functionality for achival of channels. As such, I created my own!

## Setup

The deployment is based on a docker image. Included is `start.sh` which should build and start the docker container locally with the `archive` volume mounted. Just replace the `DISCORD_TOKEN` environment variable in the `Dockerfile` to use it.