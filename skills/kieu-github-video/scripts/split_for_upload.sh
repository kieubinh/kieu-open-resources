#!/bin/sh
# Split an MP4 into 9 MB parts for the Claude-in-Chrome file bridge (limit: 10 MB per call, summed per call).
# Usage: split_for_upload.sh <video.mp4> <outdir> <prefix>     -> <outdir>/<prefix>_a, _b, ...
# Prints the byte total and verifies that the parts concatenate back to the original.
set -e
[ $# -eq 3 ] || { echo "usage: $0 <video.mp4> <outdir> <prefix>" >&2; exit 2; }
mkdir -p "$2"
split -b 9000000 -a 1 "$1" "$2/$3_"
cat "$2/$3_"* | cmp - "$1" && echo "OK: $(ls "$2/$3_"* | wc -l | tr -d ' ') parts, $(wc -c < "$1" | tr -d ' ') bytes, reassembles byte for byte"
