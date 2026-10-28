#!/usr/bin/env bash
# Replays the Vietnamese document QA discovery scenario against a COPY of the registry,
# so the committed registry is never modified. Requires only the installed CLI (or PYTHONPATH=src).
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
WORK="$(mktemp -d)"
cp -R "$REPO/registry" "$WORK/registry"
mkdir "$WORK/project"
K="${KIEU_CLI:-python3 -m kieu_open_resources.cli}"
export PYTHONPATH="$REPO/src${PYTHONPATH:+:$PYTHONPATH}"
run() { echo; echo "\$ kieu-open-resources $*"; $K "$@" --registry "$WORK/registry"; echo "[exit $?]"; }

run search "vietnamese document" --type dataset --task question-answering --language vi --status approved
run search "vietnamese" --type model --language vi --status approved
echo; echo "# Registry has nothing eligible -> do NOT invent a resource. After external discovery, submit a candidate:"
run submit-candidate "$HERE/candidate.example.json"
run search "vietnamese" --type dataset --status approved
run manifest add example-vi-docqa-dataset --project "$WORK/project"
run validate
echo; echo "Candidate file written to: registry/candidates/example-vi-docqa-dataset.json (in the temp copy $WORK)"
