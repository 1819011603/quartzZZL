#!/bin/zsh
# 用法: toggle.sh <detailV2> <preheatV2> <cacheEnabled>   只改 TEST default cluster
set -e
K1=$(sed -n 1p /tmp/w1func/keys.txt); K2=$(sed -n 2p /tmp/w1func/keys.txt); K3=preheat.cache.enabled
cd ~/.local/mcp-servers
m(){ sed -E "s/$K1/DETAIL_V2/g; s/$K2/PREHEAT_V2/g"; }
./mcpcli.py apollo_config apollo_set_key -k app_id=cart.gaotu100.com -k env=TEST -k key=$K1 -k value=$1 -k comment="W1功能对照" 2>&1 | m | tail -1
./mcpcli.py apollo_config apollo_set_key -k app_id=cart.gaotu100.com -k env=TEST -k key=$K2 -k value=$2 -k comment="W1功能对照" 2>&1 | m | tail -1
./mcpcli.py apollo_config apollo_set_key -k app_id=cart.gaotu100.com -k env=TEST -k key=$K3 -k value=$3 -k comment="W1功能对照" 2>&1 | m | tail -1
./mcpcli.py apollo_config apollo_release -k app_id=cart.gaotu100.com -k env=TEST -k comment="W1功能对照" 2>&1 | m | grep -i -E "release|发布|变更|无变更" | head -4
./mcpcli.py apollo_config apollo_get_key -k app_id=cart.gaotu100.com -k env=TEST -k "keys=[\"$K1\",\"$K2\",\"$K3\"]" 2>&1 | m | grep '^- '
