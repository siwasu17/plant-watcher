# -*- coding: utf-8 -*-
from __future__ import print_function
import httplib2
import os
import sys
import io
 
from glob import glob
from apiclient import discovery
from apiclient.http import MediaIoBaseDownload
from oauth2gdrive import get_credentials
 
# OAuth 2.0で設定するApplication ID
APPLICATION_NAME = 'my-drive-client'
# OAuth 2.0で設定するSCOPE：Google Driveにおいてファイル単位のアクセスを許可
SCOPES = 'https://www.googleapis.com/auth/drive.file'
 
# アップロードするファイルが格納されているディレクトリ
IMG_DIR = 'images'
# アップロードするファイルの拡張子
FILE_EXTENSION = 'jpg'
# ファイルを格納するGoogle Driveのフォルダ
DRIVE_DIR = 'TL_CORRECT'
# Google DriveのフォルダのmimeType
FOLDER_MIME_TYPE = 'application/vnd.google-apps.folder'
FILE_MIME_TYPE = 'application/vnd.google-apps.file'
# アップロードするファイルのmimeType
FILE_MIME_TYPE = 'image/jpeg'


def download_file(output_dir,file_name,file_id):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.FileIO(output_dir + '/' + file_name, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download {0}%.".format(int(status.progress() * 100)))


def get_folder_id(service):
    query = "mimeType='" + FOLDER_MIME_TYPE + "'" + " and name='" + DRIVE_DIR + "'"
    response = drive_service.files().list(q=query,
                                         spaces='drive',
                                         fields='files(id, name)').execute()
    for folder in response.get('files', []):
        return folder.get('id')
 
def list_files(service,since='2017-12-01T00:00:00'):
    folder_id = get_folder_id(service)
    query = "mimeType='" + FILE_MIME_TYPE + "'" + " and '{0}' in parents".format(folder_id)
    query += " and modifiedTime > '{0}'".format(since)
    print(query)
    results = service.files().list(q=query,pageSize=1000,
        orderBy="createdTime",
        fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    return items
 
if __name__ == '__main__':
    # OAuth 2.0の認証プロセスを実行する
    credentials = get_credentials(APPLICATION_NAME, SCOPES)
    http = credentials.authorize(httplib2.Http())
    drive_service = discovery.build('drive', 'v3', http=http)
    items = list_files(drive_service)
    for item in items:
        print(item)
        download_file('./download/',item['name'],item['id'])
 
