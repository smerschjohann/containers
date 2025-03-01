#!/bin/bash

if [ -n "$PROVISION_SCRIPT" ]; then
    echo "Running configured provision script"
    curl -kfsSL "$PROVISION_SCRIPT" -o /tmp/provision_script.sh
    chmod +x /tmp/provision_script.sh
    /tmp/provision_script.sh
fi

