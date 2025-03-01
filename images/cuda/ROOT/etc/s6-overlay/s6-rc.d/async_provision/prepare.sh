#!/bin/bash

if [ -n "$ASYNC_PROVISION_SCRIPT" ]; then
    echo "Running configured provision script"
    curl -kfsSL "$ASYNC_PROVISION_SCRIPT" -o /tmp/async_provision_script.sh
    chmod +x /tmp/async_provision_script.sh
    /tmp/async_provision_script.sh
fi

