#!/bin/bash

cd ./static
wget https://github.com/twbs/bootstrap/releases/download/v5.0.0-beta1/bootstrap-5.0.0-beta1-dist.zip
unzip bootstrap-5.0.0-beta1-dist.zip
mv bootstrap-5.0.0-beta1-dist bootstrap-5.0.0
rm bootstrap-5.0.0-beta1-dist.zip
wget https://github.com/weareoutman/clockpicker/archive/refs/tags/v0.0.7.zip
unzip v0.0.7.zip
mv clockpicker-0.0.7 clockpicker
rm v0.0.7.zip
cd ..

