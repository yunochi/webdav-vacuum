from webdav4.client import Client
from datetime import date
import datetime
import re
import os
import sys

try:
    webdav_id = os.environ['WEBDAV_ID']
    webdav_pass = os.environ['WEBDAV_PASS']
    webdav_path = os.environ['WEBDAV_PATH']
    webdav_endpoint = os.environ['WEBDAV_ENDPOINT']
except KeyError:
    print('Set WEBDAV_ID, WEBDAV_PASS, WEBDAV_PATH, WEBDAV_ENDPOINT env')
    sys.exit(-1)


re_date_format = r'(\d{4})-(\d{2})-(\d{2})'
retention_days = 30
client = Client(webdav_endpoint, auth=(webdav_id, webdav_pass))

file_list = client.ls(webdav_path)
backup_file_list = []

for file in file_list:
    print(f"find {file['name']}")
    try:
        # date format이 있는 파일들만 찾기
        match = re.search(re_date_format, file['name'])
        if match is None:
            continue
        match_string = match.group()
        backup_file_list.append((date.today() - date.fromisoformat(match_string), file))
    except ValueError as e:
        print(e)

# date로 정렬
# 오래된것부터 최신순으로
backup_file_list.sort(key=lambda x: x[0], reverse=True)
# 최신것 하나는 무조껀 남기게끔
print(f"preserve last file {backup_file_list[-1][1]['name']}")
backup_file_list = backup_file_list[:-1]

for timedelta, backup_file in backup_file_list:
    if timedelta > datetime.timedelta(days=retention_days):
        print(f"remove {backup_file['name']}")
        client.remove(backup_file['name'])
