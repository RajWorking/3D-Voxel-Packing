FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-numpy \
    tmux \
    asciinema \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -s /bin/bash user

RUN mkdir -p /task
COPY objects.json /task/objects.json
COPY tools/ /task/tools/
COPY instruction.md /task/instruction.md

WORKDIR /home/user
