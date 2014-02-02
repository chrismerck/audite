export RATE=8000
cat tmp.raw | play -t raw -e float -c 1 -b 32 -r$RATE - 2> /dev/null
