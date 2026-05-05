#!/bin/sh
set -eu

: "${API_HOST:=triage-backend}"
: "${API_SCHEME:=http}"
export API_HOST API_SCHEME

envsubst '${API_HOST} ${API_SCHEME}' \
  < /etc/nginx/nginx.conf.template \
  > /etc/nginx/nginx.conf

exec nginx -g 'daemon off;'
