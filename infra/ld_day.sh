#!/bin/bash
# cutover-aware day index; SAME constants as gateway (GW_GENESIS / GW_DAY_CUTOVER).
OLD=1789102088; CUT=1790726400; D=86400
NOW=$(date +%s)
DC=$(( (CUT - OLD - 1) / D + 1 ))
if [ "$NOW" -lt "$CUT" ]; then CUR=$(( (NOW - OLD) / D )); else CUR=$(( DC + (NOW - CUT) / D )); fi
case "$1" in
  prev|yesterday) echo $((CUR - 1));;
  *) echo "$CUR";;
esac
