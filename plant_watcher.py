#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import httplib2
import os
import shutil
import sys
import argparse

from glob import glob
from apiclient import discovery
from apiclient.http import MediaFileUpload
from oauth2gdrive import get_credentials
from vision import get_labels
 
# OAuth 2.0で設定するApplication ID
APPLICATION_NAME = 'my-drive-client'
# OAuth 2.0で設定するSCOPE：Google Driveにおいてファイル単位のアクセスを許可
SCOPES = 'https://www.googleapis.com/auth/drive.file'
 
# アップロードするファイルが格納されているディレクトリ
IMG_DIR = 'images'
# アップロードするファイルの拡張子
FILE_EXTENSION = 'jpg'
# ファイルを格納するGoogle Driveのフォルダ
# 全画像を入れるフォルダ
DRIVE_DIR_ALL = 'TL_ALL'
# 検知したい物体が写っている画像だけを入れるフォルダ
DRIVE_DIR_CORRECT = 'TL_CORRECT'
# Google DriveのフォルダのmimeType
FOLDER_MIME_TYPE = 'application/vnd.google-apps.folder'
# アップロードするファイルのmimeType
FILE_MIME_TYPE = 'image/jpeg'

# 検知したい物体のラベル名
CORRECT_LABELS = ['flowerpot','houseplant','plant','bonsai','wood']

def create_folder(drive_service,dir_name):
    ''' Google Driveにアップロードするファイルを格納するフォルダを作成する '''
    # 指定のフォルダが存在するかを問い合わせる
    query = "mimeType='" + FOLDER_MIME_TYPE + "'" + " and name='" + dir_name + "'"
    response = drive_service.files().list(q=query,
                                         spaces='drive',
                                         fields='files(id, name)').execute()
    for folder in response.get('files', []):
        # 指定のフォルダが存在する場合は、そのフォルダIDを返却し復帰する
        print('Folder already exists:' + folder.get('name'))
        return folder.get('id')
 
    # 指定のフォルダを新規に作成し、そのフォルダIDを返却する
    folder_metadata = {
        'mimeType': FOLDER_MIME_TYPE,
        'name': dir_name,
    }
    folder = drive_service.files().create(body=folder_metadata,
                                        fields='id, name').execute()
    print('Folder created:' + folder.get('name'))
    return folder.get('id')
 
def upload_file(drive_service, drive_folder_id, upload_file_path):
    ''' Google Driveの指定したフォルダにファイルをアップロードする
 
    アップロードするファイル名が、Google Driveに存在するかをチェックする
    ・ファイル名が存在しない場合は、指定のファイルをアップロードする
    ・ファイル名が存在する場合は、指定のファイルのアップロードをスキップする
 
    Returns: void
    '''
 
    # upload_file_pathがらファイル名を抽出する
    file_name = os.path.split(upload_file_path)[-1]
 
    # アップロードするファイル名が存在するかを問い合わせる
    query = "'" + drive_folder_id + "' in parents and mimeType='" + FILE_MIME_TYPE + "' and name='" + file_name + "'"
    response = drive_service.files().list(q=query,
                                         spaces='drive',
                                         fields='files(id, name)').execute()
    for upload_file in response.get('files', []):
        # ファイル名が存在する場合は、アップロードをスキップし復帰する
        print('File already exists:' + upload_file.get('name'))
        return
 
    # Google Driveの指定したフォルダへファイルをアップロードする
    media = MediaFileUpload(upload_file_path, mimetype=FILE_MIME_TYPE, resumable=True)
    file_metadata = {
        'mimeType': FILE_MIME_TYPE,
        'name': file_name,
        'parents': [drive_folder_id],
    }
    created_file = drive_service.files().create(body=file_metadata,
                                                media_body=media,
                                                fields='id, name').execute()
    print('Upload sucssesful:' + created_file.get('name'))


def upload_files(watch_dir):
    # OAuth 2.0の認証プロセスを実行する
    credentials = get_credentials(APPLICATION_NAME, SCOPES)
    http = credentials.authorize(httplib2.Http())
    drive_service = discovery.build('drive', 'v3', http=http)
    folder_all = create_folder(drive_service,DRIVE_DIR_ALL)
    folder_correct = create_folder(drive_service,DRIVE_DIR_CORRECT)

    trash_dir = watch_dir + '/trash'
    if not os.path.exists(trash_dir):
        os.mkdir(trash_dir)

    upload_files_path = glob(os.path.join(watch_dir, '*.' + FILE_EXTENSION))
    if not upload_files_path:
        # 該当するファイルが存在しない場合は終了する
        print('File does not exist. It does not upload.')
        sys.exit()

    for file_path in upload_files_path:
        print('Upload file:' + file_path)
        # とりあえず全部入れる
        upload_file(drive_service, folder_all, file_path)
        labels = get_labels(file_path)
        print(labels)
        for l in labels:
            if l.description in CORRECT_LABELS:
                print('OK :' + file_path)
                # 正解は分けて入れる
                upload_file(drive_service, folder_correct, file_path)
                break
        # 処理が終わったら移動しておく
        shutil.move(file_path,trash_dir)
 
if __name__ == '__main__':
    upload_files("./images")
