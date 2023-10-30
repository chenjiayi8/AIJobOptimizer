
FROM ubuntu:22.04

ENV DOCKER_GID=1000
ENV DOCKER_UID=1000
ENV TZ=UTC

# install common tools
RUN apt update
RUN apt install -y bash sudo

# replace shell with bash so we can source files
RUN rm /bin/sh && ln -s /bin/bash /bin/sh

# timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt update && apt install -y git nano htop wget
RUN apt update && apt install -y build-essential linux-headers-generic
RUN apt install -y python3-dev python3-pip
RUN apt install -y libxcb-xinerama0 libxkbcommon-x11-0 libxcb-icccm4 libxcb-image0 libxcb-util1 libxcb-keysyms1 libxcb-render-util0
RUN apt install -y qttools5-dev-tools tree


# add user vscode with same uid and gid
RUN groupadd -g $DOCKER_GID vscode
RUN useradd vscode -u $DOCKER_UID -g $DOCKER_GID --create-home -m -s /bin/bash

# add user vscode to sudoers
RUN echo "vscode ALL=(ALL) NOPASSWD: ALL" | tee /etc/sudoers.d/vscode
RUN chmod 0440 /etc/sudoers.d/vscode




# install virtualenv
RUN pip install virtualenv


USER vscode

WORKDIR /home/vscode

# Copy requirements.txt from local machine to container
COPY --chown=vscode:vscode ./requirements.txt /home/vscode/

# Create a new virtual environment
RUN virtualenv --python=python3.10 /home/vscode/env
RUN source /home/vscode/env/bin/activate

# Enable venv
ENV PATH="/home/vscode/env/bin:$PATH"

# Install dependencies from requirements.txt
RUN pip install -r /home/vscode/requirements.txt

RUN mkdir -p /home/vscode/.config

ENV NODE_VERSION=16.13.0
ENV NVM_DIR=/home/vscode/nvm
RUN mkdir -p $NVM_DIR
RUN git clone https://github.com/nvm-sh/nvm.git "$NVM_DIR" \
    && cd "$NVM_DIR" \
    && git checkout `git describe --abbrev=0 --tags --match "v[0-9]*" $(git rev-list --tags --max-count=1)` \
    && \. "$NVM_DIR/nvm.sh"
# install node and npm
RUN source $NVM_DIR/nvm.sh \
    && nvm install $NODE_VERSION \
    && nvm alias default $NODE_VERSION \
    && nvm use default

# add node and npm to path so the commands are available
ENV NODE_PATH $NVM_DIR/v$NODE_VERSION/lib/node_modules
ENV PATH $NVM_DIR/versions/node/v$NODE_VERSION/bin:$PATH
# install aicommits and pm2
RUN npm install -g aicommits pm2


RUN echo "alias ll='ls -alFh'" >> /home/vscode/.bashrc
RUN echo "export LIBGL_ALWAYS_SOFTWARE=1" >> /home/vscode/.bashrc
