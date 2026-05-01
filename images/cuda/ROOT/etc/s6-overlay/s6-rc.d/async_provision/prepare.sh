#!/bin/bash

# Check if async provision script is mounted as a volume
if [ -f "/provision/async_provision_script.sh" ]; then
    echo "Running async provision script from volume mount"
    chmod +x /provision/async_provision_script.sh
    /provision/async_provision_script.sh
# Otherwise, check if an async provision script URL is configured
elif [ -n "$ASYNC_PROVISION_SCRIPT" ]; then
    echo "Running configured provision script"
    CURL_OPTS=(-kfsSL)
    if [ -n "$ASYNC_PROVISION_SCRIPT_TOKEN" ]; then
        CURL_OPTS+=(-H "Authorization: Bearer $ASYNC_PROVISION_SCRIPT_TOKEN")
    fi
    curl "${CURL_OPTS[@]}" "$ASYNC_PROVISION_SCRIPT" -o /tmp/async_provision_script.sh
    chmod +x /tmp/async_provision_script.sh
    /tmp/async_provision_script.sh
fi

