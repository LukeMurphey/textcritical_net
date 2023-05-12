#!/bin/sh
cd /git/textcritical_net/
git submodule update

cd /git/textcritical_net/submodules/textcritical_spa
yarn run build
