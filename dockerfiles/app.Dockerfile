FROM ubuntu:20.04
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update
RUN apt-get -y install sudo
RUN apt-get install -y \
    python3.8 \
    python3-pip \
    libgl1-mesa-dev \
    libglib2.0-0 \
    libpq-dev \
    && pip3 install poetry

RUN \
    groupadd -g 999 dckr && useradd -u 999 -g dckr -G sudo -m -s /bin/bash dckr && \
    sed -i /etc/sudoers -re 's/^%sudo.*/%sudo ALL=(ALL:ALL) NOPASSWD: ALL/g' && \
    sed -i /etc/sudoers -re 's/^root.*/root ALL=(ALL:ALL) NOPASSWD: ALL/g' && \
    sed -i /etc/sudoers -re 's/^#includedir.*/## **Removed the include directive** ##"/g' && \
    echo "dckr ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers && \
    echo "Customized the sudoers file for passwordless access to the dckr user!" && \
    echo "dckr user:";  su - dckr -c id

USER dckr

COPY pyproject.toml ./
COPY poetry.lock ./
RUN poetry install --verbose

RUN sudo apt-get install -y p7zip-full
RUN sudo apt-get install -y git

# COPY setup_model.sh ./
# RUN /setup_model.sh
RUN echo "Downloading model files..."
RUN git clone https://github.com/jeremyleonardo/insightface-models.git
RUN echo "Merging zip files..."
RUN cat ./insightface-models/models.zip.* > ./models.zip
RUN echo "Extracting..."
RUN 7z -y x models.zip -o"./models"
RUN mkdir -p ~/.insightface/models
RUN cp -r ./models ~/.insightface/models
RUN echo "Model files extracted to ~/.insightface/models"

COPY init_model.py ./
RUN poetry run python init_model.py

COPY ./app /app
