# root-notice.sh: printed at an interactive root login on the lab machines (install as
# /etc/profile.d/zz-lab-root-notice.sh, 0644 root). Since 2 October 2026 new people get the shared root login, only to
# create their own account; work done as root cannot be told apart from other people's, on the cards or in the logs.
if [ "$(id -u)" = 0 ] && [ -n "${PS1:-}" ]; then
  printf '\n*** You are logged in as root, the lab'"'"'s SHARED login. ***\n'
  printf 'Use it only to create your own account (step 1 of https://spacesheep.dev/@yaroslavvb/aifoundry-lab-start),\n'
  printf 'then log out and work as yourself: what you run as root cannot be told apart from anyone else'"'"'s.\n\n'
fi
