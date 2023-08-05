#!/bin/sh

set -e

RUN git clone https://github.com/jeremyleonardo/insightface-models.git
RUN echo "Merging zip files..."
RUN cat ./insightface-models/models.zip.* > ./models.zip
RUN echo "Extracting..."
RUN 7z -y x models.zip -o"./models"
RUN mkdir -p ~/.insightface
RUN cp -r ./models ~/.insightface
RUN echo "Model files extracted to ~/.insightface/models"