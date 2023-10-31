FROM ubuntu:22.04 as compiler
ENV TZ=UTC
ENV PYTHON_VERSION=3.9.0

# timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# install common tools
RUN apt update
RUN apt install -y make build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev \
liblzma-dev git bash

# Install pyenv
ENV PYENV_ROOT="/pyenv"
ENV PATH "$PYENV_ROOT/bin:$PATH"
ENV eval "$(pyenv init -)"
RUN curl https://pyenv.run | bash

# Install python version
RUN pyenv install $PYTHON_VERSION
ENV PATH="/pyenv/versions/${PYTHON_VERSION}/bin:$PATH"

# Install virtualenv
RUN pip install virtualenv

FROM ubuntu:22.04 as development
COPY --from=compiler /pyenv /pyenv
ENV TZ=UTC
ENV PYTHON_VERSION=3.9.0
ENV NODE_VERSION=16.13.0
ENV DOCKER_GID=1000
ENV DOCKER_UID=1000

ENV PATH="/pyenv/versions/${PYTHON_VERSION}/bin:$PATH"

# install common tools
RUN apt update
RUN apt install -y bash sudo

# replace shell with bash so we can source files
RUN rm /bin/sh && ln -s /bin/bash /bin/sh

# timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt update && apt install -y git nano htop wget tree
RUN apt install -y build-essential libssl-dev

# add user vscode with same uid and gid
RUN groupadd -g $DOCKER_GID vscode
RUN useradd vscode -u $DOCKER_UID -g $DOCKER_GID --create-home -m -s /bin/bash

# add user vscode to sudoers
RUN echo "vscode ALL=(ALL) NOPASSWD: ALL" | tee /etc/sudoers.d/vscode
RUN chmod 0440 /etc/sudoers.d/vscode

USER vscode
WORKDIR /home/vscode

# Create a new directory for vscode config
RUN mkdir -p /home/vscode/.config

# Copy requirements.txt from local machine to container
COPY --chown=vscode:vscode ./requirements.txt /home/vscode/

# Create a new virtual environment
RUN virtualenv -p=/pyenv/versions/${PYTHON_VERSION}/bin/python /home/vscode/env
RUN source /home/vscode/env/bin/activate

# Enable venv
ENV PATH="/home/vscode/env/bin:$PATH"

# Install dependencies from requirements.txt
RUN pip install -r /home/vscode/requirements.txt

# Install nodejs
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

# add helpful aliases
RUN echo "alias ll='ls -alFh'" >> /home/vscode/.bashrc
