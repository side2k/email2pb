import argparse
import base64
import email
import json
import re
from subprocess import Popen, PIPE, STDOUT
import sys

CURL_PROGRAM = 'curl'
API_URL = 'https://api.pushbullet.com/api/pushes'
PUSH_TYPE = 'note'

TRACE_FILE = 'curl.trace'

parser = argparse.ArgumentParser(description='Send PushBullet PUSH based on email message')
parser.add_argument('infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin,
    help='MIME-encoded email file(if empty, stdin will be used)')
parser.add_argument('--key', help='API key for PushBullet', required=True)
parser.add_argument('--debug', help='Enable debug mode', action='store_true')
args = parser.parse_args()
debug_mode = args.debug
if debug_mode:
    print 'Debug mode enabled'

msg = email.message_from_file(args.infile)
args.infile.close()

subject_raw = msg.get('Subject', '')
match = re.match(r'\=\?([^\?]+)\?([BQ])\?([^\?]+)\?\=', subject_raw)
if match:
    charset, encoding, subject_coded = match.groups()
    if encoding == 'B':
        subject_coded = base64.decodestring(subject_coded)
    subject = subject_coded.decode(charset)
else: 
    subject = subject_raw
body_text = ''
for part in msg.walk():
    if part.get_content_type() == 'text/plain':
        body_part = part.get_payload()
        if part.get('Content-Transfer-Encoding', 'base64') == 'base64':
            body_part = base64.decodestring(body_part)

        if body_text:
            body_text = '%s\n%s' % (body_text, body_part)
        else:
            body_text = body_part

push_headers = {
    'type': PUSH_TYPE,
    'title': subject,
    'body': body_text,
}

program = CURL_PROGRAM
cmdline = [program, API_URL, '-s', '-u', '%s:' % args.key, '-X', 'POST']
header_pairs = [['-d', '%s=%s' % (header, data)] for header, data in push_headers.iteritems()]
cmdline += [item.encode() for sublist in header_pairs for item in sublist]
if debug_mode:
    cmdline += ['--trace-ascii', TRACE_FILE]
    print 'Command line:'
    print '----------'
    print ' '.join(cmdline)
    print '----------'

process = Popen(cmdline, stdout=PIPE, stderr=STDOUT)
stdout, stdin = process.communicate()
exit_code = process.returncode
if exit_code:
    print '%s returned exit code %d' % (program, exit_code)
    print 'Output:'
    print '---------'
    print stdout
    print '---------'
    sys.exit(exit_code)
else:
    try:
        server_response = json.loads(stdout)
    except:
        if debug_mode:
            print 'Server response was not JSON:'
            print '--------------'
            print stdout
            print '--------------'
        raise
    error = server_response.get('error')
    if error:
        print 'Server returned error:'
        print error.get('message')
        sys.exit(1)
