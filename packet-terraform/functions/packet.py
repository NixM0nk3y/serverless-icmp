"""

"""
import boto3
import json
import os
import sys
import logging
import botocore
import pickle
import base64
import zlib

from scapy.all import *

from boto3.session import Session
from botocore.exceptions import ClientError
from lambda_logging import logged_handler, setup_lambda_logger

#
LOGLEVEL = os.environ['LOGLEVEL']

# Configure a python logger for use with lambda
LOGGER = setup_lambda_logger()

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

def build_echo_reply(packet):

    ip = IP()
    icmp = ICMP()
    ip.src = packet[IP].dst
    ip.dst = packet[IP].src
    icmp.type = 0
    icmp.code = 0
    icmp.id = packet[ICMP].id
    icmp.seq = packet[ICMP].seq
    LOGGER.info("Sending back an echo reply to %s" % ip.dst)
    data = packet[ICMP].payload

    return ip/icmp/data

@logged_handler(LOGGER)
def lambda_handler(event, context):

    response = {
        'reply': False,
    }

    LOGGER.debug("Received Event: {}".format(json.dumps(event)))
    try:

        packet = native_object_decoded(event['packet'])

        proto = packet.proto

        if proto is 0x01:
            LOGGER.info("It's an ICMP packet")

            # Idea: intercept an echo request and immediately send back an echo reply packet
            if packet[ICMP].type is 8:
                LOGGER.info("It's an ICMP echo request packet")
                
                response = {
                'reply': True,
                'packet': native_object_encoded(build_echo_reply(packet))
                }

            else:
                pass

    except Exception as e:
        # If any other exceptions which we didn't expect are raised
        # then fail the job and log the exception message.
        LOGGER.error('Function failed due to exception:{}'.format(e)) 

    return response