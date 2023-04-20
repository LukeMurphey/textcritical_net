#!/bin/sh
cd /git/textcritical_spa

# Run yarn install in case something has changed
yarn install

# We are using 'start_listen_all' need to have webpack not restrict itself to local host because
# inbound network connections are coming through Docker's bridge which will appear to be an external
# host
yarn run start_listen_all
