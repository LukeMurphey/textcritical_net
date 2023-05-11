#!/bin/bash
cd /git/textcritical_net
ant test

BACKEND=$?

cd /git/textcritical_net/submodules/textcritical_spa
yarn run test

FRONTEND=$?

if [ $BACKEND -eq 0 ]; then
    echo "✅ Backend tests passed"
else
    echo "⛔ Backend tests failed"
fi

if [ $FRONTEND -eq 0 ]; then
    echo "✅ Frontend tests passed"
else
    echo "⛔ Frontend tests failed"
fi
