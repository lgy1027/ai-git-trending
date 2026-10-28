#!/bin/sh
set -eu

: "${VITE_API_BASE_URL:=}"
export VITE_API_BASE_URL

envsubst '${VITE_API_BASE_URL}' \
  < /etc/nginx/runtime-config.js.template \
  > /usr/share/nginx/html/runtime-config.js
