import argparse
import base64
import email
import io
import logging
import os
import re
import sys

from datetime import date
from logging.handlers import RotatingFileHandler
from pushbullet import Pushbullet


# Read arguments
parser = argparse.ArgumentParser(description="Send PushBullet PUSH based on email message")
parser.add_argument(
    "infile", 
    nargs="?", 
    type=argparse.FileType("r"), 
    default=sys.stdin,
    help="MIME-encoded email file(if empty, stdin will be used)")
parser.add_argument("--key", help="API key for PushBullet", required=True)
parser.add_argument("--log_level", default="40", help="10=debug 20-info 30=warning 40=error", type=int)
parser.add_argument("--log_file", default="email2pb.log", help="Log file location", type=str)
args = parser.parse_args()

# Configure logging
logger = logging.getLogger(__name__)
handler = RotatingFileHandler(args.log_file, mode='a', maxBytes=1024*1024, backupCount=1)
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(handler) 
logger.setLevel(args.log_level)
logger.debug(args)

# Read infile (is stdin if no arg) 
stdin_data = args.infile.read()
args.infile.close()
logger.debug("in:\n" + stdin_data)
msg_parts = email.message_from_string(stdin_data).get_payload()

# Parse out the text
html = msg_parts[0].get_payload()
clean_html = re.sub(r"(?is)<(script|style).*?>.*?(</\1>)", "", html.strip()) # Remove style tags
text = re.sub(r"(?s)<.*?>", " ", clean_html).strip() # Get text content
logger.debug("Found text: " + text)

# Hardcoded: Only interested in channel 2
if(not re.findall("Event:Motion detect in video channel 2", text)):
    logger.error("Not channel 2: " + text)
    quit()

# Parse the base64 image data and upload to pushbullet
image_part = msg_parts[1].get_payload()
file_name = date.today().strftime("%Y-%m-%d") + "_" + re.findall("name=\"(.*?)\"", msg_parts[1]["Content-Type"])[0]
file = io.BytesIO(image_part.decode('base64'))
logger.debug("Uploading " + file_name)
pb = Pushbullet(args.key)
file_data = pb.upload_file(file, file_name)

# Send push
logger.debug("Sending push")
push = pb.push_file(body = text, **file_data)

logger.info("Successfully pushed: " + text)
