import argparse
import base64
import email
import io
import logging
import os
import re
import sys

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
logger.debug("\n" + stdin_data)

# Parse stdin
pb = Pushbullet(args.key)
parts = stdin_data.split("--=======JUAN_SMTP_V1_0=======")

# Parse out the text
text = parts[0]
text = re.findall("\n\n(.*)", text)[0] # Remove header info
text = re.sub(r"(?is)<(script|style).*?>.*?(</\1>)", "", text.strip()) # Remove style tags
text = re.sub(r"(?s)<.*?>", " ", text).strip() # Get text content
logger.debug("Found text: " + text)

# Hardcoded: Only interested in channel 2
if(not re.findall("Event:Motion detect in video channel 2", text)):
    logger.error("Not channel 2: " + text)
    # quit()

# Parse the base64 image data and upload to pushbullet
image_part = parts[1]
file_name = re.findall("name=\"(.*?)\"", image_part)[0]
base64_data = re.findall("\n\n(.*)", image_part)[0].strip()
file = io.BytesIO(base64_data.decode('base64'))
logger.debug("Uploading " + file_name)
# file_data = pb.upload_file(file, file_name)

# Send push
logger.debug("Sending push")
# push = pb.push_file(body = text, **file_data)

logger.info("Successfully pushed: " + text)
