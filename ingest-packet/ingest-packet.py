#!/usr/bin/python3
#
#
#

import subprocess
import argparse
import logging
import boto3
import json
import sys
import os
import pickle
import base64
import zlib

from botocore.exceptions import ClientError

from scapy.all import *
from netfilterqueue import NetfilterQueue

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%dT%H:%M:%S%z', level=logging.INFO)

client = boto3.client('lambda')

def native_object_decoded(s):
    s = base64.b64decode(s)
    s = zlib.decompress(s)
    s = pickle.loads(s)
    return s

def native_object_encoded(x):
    x = pickle.dumps(x)
    x = zlib.compress(x)
    x = base64.b64encode(x).decode()
    return x

def send_packet(packet):

    send(packet, verbose=0)

    return

def callback(packet):

    logging.debug('packet callback')

    logging.debug(packet)

    try:
        response = client.invoke(
            FunctionName='dev-packet',
            InvocationType='RequestResponse',
            Payload=json.dumps({
                "packet": native_object_encoded(packet)
            })
        )

        if 'Payload' in response:

            result = json.loads(response['Payload'].read().decode())

            logging.info(result)

            if result['reply']:

                reply_packet = native_object_decoded( result['packet'] )

                send_packet(reply_packet)
 
    except ClientError as e:
        logging.error("Error invoking lambda:{0}".format(e))
    except ValueError as e:
        logging.error("Error decoding result:{0}".format(e))

    return

def process(packet):

    pkt = IP(packet.get_payload()) #converts the raw packet to a scapy compatible string

    callback(pkt)

    #packet.set_payload(pkt) #set the packet content to our modified version

    packet.drop() # drop the packet - we'll process elsewhere

    return

def ingest(args):
    """
    """

    nfqueue = NetfilterQueue()
    nfqueue.bind(args.queue, process) 

    try:
        logging.info("Waiting for network data")
        nfqueue.run()

    except KeyboardInterrupt:
        pass

    return

if __name__== "__main__":
  
    parser = argparse.ArgumentParser(prog='ingest_packet')

    parser.add_argument('--queue', '-q', default=1)
    parser.add_argument('--verbose', '-v', action='count', default=0)

    args = parser.parse_args()

    if args.verbose:
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

    ingest(args)

