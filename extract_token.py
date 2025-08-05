#! /usr/bin/env python3

import argparse
import os
import sqlite3
import tempfile
import shutil
import json
import snappy

parser = argparse.ArgumentParser()
parser.add_argument('--token-file', default="tokens.json", help='File to save extracted token values to')
parser.add_argument('--firefox-dir', type=str, default="~/.mozilla/firefox", help="Firefox storage directory")
parser.add_argument('--profile-name', type=str, default=None, help="Profile to use (if not firefox default)")

args = parser.parse_args()

firefox_dir = os.path.expanduser(args.firefox_dir)

# Either use provided profile or the default one
profile_name = args.profile_name
if profile_name is None:
    with open(os.path.join(firefox_dir, "profiles.ini"), 'r') as file:
        for line in file:
            search_pattern = 'Default='
            if line.startswith(search_pattern):
                profile_name = line[len(search_pattern):].strip()
                break

assert(profile_name)

db_path=os.path.join(firefox_dir, profile_name, "storage/default/https+++www.hochschulsportmuenster.de/ls/data.sqlite")

tmp_file = tempfile.NamedTemporaryFile(delete=True)
db_copy = tmp_file.name
shutil.copy2(db_path, db_copy)

db = sqlite3.connect(db_copy)

cur = db.cursor()
res = cur.execute("select value, compression_type from data where key='delcom_auth'")
response, compression = res.fetchone()
if compression == 1:
    response = snappy.decompress(response)
response = json.loads(response.decode('utf8'))
tokens = response['tokenResponse']

print("Extracted tokens: {}".format(tokens))
with open(args.token_file, "w") as out_file:
    out_file.write(json.dumps(tokens))
