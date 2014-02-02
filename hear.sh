export RATE=8000
rec -t raw -e float -c 1 -b 32 -r$RATE - 2> /dev/null | python hear.py "$@"
exit $?
