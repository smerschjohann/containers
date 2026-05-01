#!/bin/bash

# Check if provision script is mounted as a volume
if [ -f "/provision/provision_script.sh" ]; then
    echo "Running provision script from volume mount"
    chmod +x /provision/provision_script.sh
    /provision/provision_script.sh
# Otherwise, check if a provision script URL is configured
elif [ -n "$PROVISION_SCRIPT" ]; then
    echo "Running configured provision script"
    CURL_OPTS=(-kfsSL)
    if [ -n "$PROVISION_SCRIPT_TOKEN" ]; then
        CURL_OPTS+=(-H "Authorization: Bearer $PROVISION_SCRIPT_TOKEN")
    fi
    curl "${CURL_OPTS[@]}" "$PROVISION_SCRIPT" -o /tmp/provision_script.sh
    chmod +x /tmp/provision_script.sh
    /tmp/provision_script.sh
fi

