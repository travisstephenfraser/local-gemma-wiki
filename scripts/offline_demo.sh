#!/bin/zsh
# Offline demonstration for the assignment. Run with Wi-Fi OFF:
#   scripts/offline_demo.sh
# Everything printed is also saved to evidence/offline/transcript.txt.
set -u
cd "${0:A:h}/.."
OUT=evidence/offline
mkdir -p "$OUT"
WIKI=.venv/bin/wiki
exec > >(tee "$OUT/transcript.txt") 2>&1

run() { print -P "\n%B\$ $*%b"; "$@"; }

print "Offline demo · $(date '+%Y-%m-%d %H:%M:%S %Z')"
if /sbin/ping -c1 -t2 1.1.1.1 >/dev/null 2>&1; then
  print "Network is ONLINE. Turn Wi-Fi off (and unplug Ethernet), then rerun."; exit 1
fi
print "Network check: 1.1.1.1 unreachable, running offline."
run networksetup -getairportpower en0
run sysctl -n machdep.cpu.brand_string hw.memsize

# restart the runtime so nothing cached from an online session is reused
run ~/.lmstudio/bin/lms server stop
run ~/.lmstudio/bin/lms server start
run ~/.lmstudio/bin/lms ls

run $WIKI --help
run $WIKI status

# ingest a new local source while offline, then again to prove re-ingest adds nothing
mkdir -p vault/raw/assign4
cp -n "feed/Assignment 4_ Personal Wiki with Local Gemma + RAG.md" vault/raw/assign4/ 2>/dev/null
run $WIKI ingest vault/raw/assign4
run $WIKI status   # memory footprint right after local ingestion
run ls vault/wiki/Projects
run $WIKI ingest
run ls vault/wiki/Projects

run $WIKI search "replay buffer capacity" -k 3
run $WIKI ask "What replay buffer capacity did the Ms. Pac-Man DQN use, and what was the notebook's default?"
run $WIKI ask "What grade did I receive on the Ms. Pac-Man assignment?"

# the four evidence cards and the chat/search/ask boundary checks, all local
run $WIKI eval --judge
run $WIKI eval --modes

# a real chat session through the CLI loop, with a follow-up
print -P "\n%B\$ wiki chat%b"
printf '%s\n' "what can you help me with?" \
  "Draft a three-step plan to review my Pac-Man project before a quiz." \
  "make that shorter" "/sources" "/exit" | $WIKI chat

print "\nDone. Transcript: $OUT/transcript.txt"
