#!/bin/sh

set -e

echo "Downloading model files..."
git clone https://github.com/jeremyleonardo/insightface-models.git
cd ./insightface-models
echo "Merging zip files..."
cat ./models.zip* > ./models.zip
echo "Extracting..."
7z -y x models.zip -o"./models"
mkdir ~/.insightface/models
cp -r ./models ~/.insightface/models
echo "Model files extracted to ~/.insightface/models"
