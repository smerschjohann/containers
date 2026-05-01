#!/bin/bash

if [ -n "$PROVISION_SCRIPT" ]; then
    echo "Running configured provision script"
    CURL_OPTS=(-kfsSL)
    if [ -n "$PROVISION_SCRIPT_TOKEN" ]; then
        CURL_OPTS+=(-H "Authorization: Bearer $PROVISION_SCRIPT_TOKEN")
    fi
    curl "${CURL_OPTS[@]}" "$PROVISION_SCRIPT" -o /tmp/provision_script.sh
    chmod +x /tmp/provision_script.sh
    /tmp/provision_script.sh
fi

