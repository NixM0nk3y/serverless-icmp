
"Serverless" ICMP Stack:

Two parts:

#1 terraform module to install a lambda to process incoming ICMP echo-requests

#2 a python script to collect the ICMP packets from the network stack via Nfqueue 

Setup:

Run the terraform found in ./packet-terraform into AWS

Add a firewall rule to the test host to capture traffic

i.e.

iptables -A INPUT -p icmp --icmp-type 8 -j NFQUEUE --queue-num 1

Run the script found in ./ingest-packet on the test host to collect the packets and send to the lambda.

n.b. assumes AWS credentials are already setup.

