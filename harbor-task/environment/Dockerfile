FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-numpy \
    && rm -rf /var/lib/apt/lists/*

# Copy task files into container
COPY . /task/

# Create working directory for agent output
RUN mkdir -p /home/user && chmod 777 /home/user

WORKDIR /home/user
