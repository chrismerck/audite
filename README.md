audite
======

Speaker and Mic Test Module

Uses DTMF tones to test transmission through an audio circuit.

NOTE: We disallow repeating digits in the DTMF strings to improve robustness of recognition.

DEPENDANCIES: python-numpy sox

usage
-----

To play some tones:
./beep.sh 123

To recognize some tones:
TIMEOUT=5 ./hear.sh 123

Returns 0 on recognition, 1 on timeout.
