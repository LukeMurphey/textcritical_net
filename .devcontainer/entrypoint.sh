#!/bin/sh


cd /workspace/submodules/textcritical_spa

while true
do
    # Run yarn install in case something has changed
    #yarn install

    # We are using 'start_listen_all' need to have webpack not restrict itself to local host because
    # inbound network connections are coming through Docker's bridge which will appear to be an external
    # host
    #yarn run start_listen_all

    # Sleep for a bit so that a problem doesn't spike the CPU usage
    sleep 3
done
