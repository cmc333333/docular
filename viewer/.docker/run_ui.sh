#!/bin/bash

set -e

if [ "$NODE_ENV" == "production" ]; then
  npm start
else
  npm run dev
fi
