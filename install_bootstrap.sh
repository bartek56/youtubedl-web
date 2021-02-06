#!/bin/bash

cd ./static
wget https://github.com/twbs/bootstrap/releases/download/v5.0.0-beta1/bootstrap-5.0.0-beta1-dist.zip
unzip bootstrap-5.0.0-beta1-dist.zip
mv bootstrap-5.0.0-beta1-dist bootstrap-5.0.0
rm bootstrap-5.0.0-beta1-dist.zip
cd ..

