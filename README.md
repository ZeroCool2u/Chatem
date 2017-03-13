Notes:

Chatem was developed using Python3 on Ubuntu 64-bit LTS.
It does not execute in Windows environments.

There is argument specific help for each script builtin to the argument parser.

Example Commands:

Directory Service Start:

<code>
python3 dirservice.py -port 9876
<code>

Chat client instance 1:

<code>
python3 chat.py -username Theo -hostaddress 127.0.0.1:54321 -destinationaddress Eve  -directoryaddress 127.0.0.1:9876
<code>

Chat client instance 2:

<code>
python3 chat.py -username Eve -hostaddress 127.0.0.1:3000 -destinationaddress Theo -directoryaddress 127.0.0.1:9876
<code>