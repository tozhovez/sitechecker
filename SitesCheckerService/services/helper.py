
import socket
import os
from datetime import datetime

import json
import signal
import urllib
from urllib.parse import urlparse
import urllib.request

from io import BytesIO
import platform
import time
import re
import os
import sys
import traceback
import subprocess
import argparse
import socket
import ssl
import dns.resolver

import asyncio
import base64



def url_id(url):
    """Generates the object ID for an URL.
    """
    return base64.urlsafe_b64encode(url.encode()).decode().strip("=")


def _make_sync(future):
    """Utility function that waits for an async call, making it sync."""
    try:
        event_loop = asyncio.get_event_loop()
    except RuntimeError:
        # Generate an event loop if there isn't any.
        event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(event_loop)
    return event_loop.run_until_complete(future)


def is_valid_tld(tld):
    try:
        dns.resolver.query(f"{tld}.", 'SOA')
        return True
    except dns.resolver.NXDOMAIN:
        return False


def isIp(value):
    """
    Checks if a value is an IP
    """
    ip_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b$'
    if re.match(ip_pattern, value):
        return True
    return False


def is_private(ip):
    """
    Checks if an IP is private
    """
    ip = IP(ip)
    if ip.iptype() == "PRIVATE":
        return True
    return False


def is_resolvable(domain):
    """
    Checks if a domain is resolvable
    """
    try:
        socket.gethostbyname(domain)
        return True
    except Exception as e:

        return False
