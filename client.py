#!/usr/bin/env python3

import urllib.request
import json as _json
import os
import argparse
from pathlib import Path
import uuid
from datetime import datetime

PER_PAGE = 200


class Client:
    url = 'https://substrate.office.com/todob2/api/v1'
    def __init__(self, bearer_token):
        self._token = bearer_token
        self._headers = {'Authorization': f'Bearer {bearer_token}'}

    def _request(self, path, data=None, json=None, headers=None, method=None):
        merged_headers = {
            **self._headers,
            **(headers or {}),
        }
        if data is None and json is not None:
            merged_headers['Content-Type'] = 'application/json'
            data = _json.dumps(json).encode()
        req = urllib.request.Request(f'{self.url}{path}', data=data, headers=merged_headers, method=method)
        with urllib.request.urlopen(req) as response:
            r = _json.loads(response.read())
        return r

    def list_folders(self):
        # TODO: handle pagination (more than 200 folders?)
        req = self._request(f'/taskfolders?$select=*,AllExtensions/Com_Wunderlist_Import,AllExtensions/com_microsoft_uno&maxpagesize={PER_PAGE}')
        folders = req['Value']
        # FIXME: check for pagination
        if len(folders) >= PER_PAGE:
            raise NotImplementedError('folder pagination required and MISSING')
        return folders

    def create_folder(self, name, theme='blue'):
        data = {'Name': name, 'OrderDateTime': datetime.now().isoformat(), 'ShowCompletedTasks': True, 'ThemeColor': theme}
        req = self._request('/taskfolders?$select=*,AllExtensions/Com_Wunderlist_Import,AllExtensions/com_microsoft_uno', json=data)
        return req
    
    def list_tasks(self, folder_id):
        req = self._request(f'/taskfolders/{folder_id}/tasks?$select=*,AllExtensions/com_microsoft_uno_richplannertask&maxpagesize={PER_PAGE}')
        tasks = req['Value']
        # FIXME: check for pagination
        if len(tasks) >= PER_PAGE:
            raise NotImplementedError('task pagination required and MISSING')
        return tasks
    
    def update_task(self, task_id: str, subject: str=None, order_date: datetime=None, due_date: datetime=None, categories: list[str] = None, body = None, body_html=True):
        data = self._task_object(subject=subject, order_date=order_date, due_date=due_date, categories=categories, body=body, body_html=body_html)
        return self._request(f'/tasks/{task_id}?$select=*,AllExtensions/com_microsoft_uno_richplannertask', json=data, method='PATCH')
    
    @staticmethod
    def _task_object(subject: str=None, order_date: datetime=None, due_date: datetime=None, categories: list[str] = None, body = None, body_html=True):
        data = {}
        if subject is not None:
            data['Subject'] = subject
        if order_date:
            data['OrderDateTime'] = order_date.isoformat()
        if due_date:
            # FIXME: hardcoded tz, quick CLI test!
            data['DueDateTime'] = {'DateTime': due_date.date().isoformat(), 'TimeZone': "Europe/Lisbon" }
        if categories is not None:
            data['Categories'] = categories
        if body:
            data['Body'] = {'Content': body, 'ContentType': 'HTML' if body_html else 'text'}
            data['BodyLastModifiedTime'] = datetime.now().isoformat()
        return data

    def create_task(self, folder_id: str, subject: str, id: str=None, order_date: datetime=None, due_date: datetime=None, categories: list[str] = None, body = None, body_html=True):
        if id is None:
            id = f'web:{str(uuid.uuid4())}'
        data = {
            'ParentFolderId': folder_id,
            'CreatedWithLocalId': id,
            'Subject': subject,
            'Importance': 'Normal',
        }
        data.update(self._task_object(order_date=order_date, due_date=due_date, categories=categories, body=body, body_html=body_html))
        req = self._request(f'/taskfolders/{folder_id}/tasks?$select=*,AllExtensions/com_microsoft_uno_richplannertask', json=data)
        return req
    
    def add_subtask(self, task_id: str, subtask: str, is_completed=False):
        data = {
            'Subject': subtask,
            'OrderDateTime': datetime.now().isoformat(),
        }
        if is_completed:
            data['IsCompleted'] = 'true'
        req = self._request(f'/tasks/{task_id}/subtasks', json=data)
        return req


def parser():
    p = argparse.ArgumentParser()
    p.add_argument('--token', default=os.getenv('TODO_TOKEN'), help='Microsoft To-Do bearer token - take it from network inspector in browser (defaults to env var TODO_TOKEN)')
    return p


def parser_parse(argv=None, p=None):
    if p is None:
        p = parser()
    args = p.parse_args(argv)
    if not args.token:
        p.error('--token or TODO_TOKEN are required')
    return args


def main(argv=None):
    args = parser_parse(argv)
    c = Client(args.token)

    TEST_FOLDER_NAME = 'ScriptTest'
    folders = c.list_folders()
    for f in folders:
        if f['Name'] == TEST_FOLDER_NAME:
            break
    else:
        f = c.create_folder(TEST_FOLDER_NAME)

    task = c.create_task(f['Id'], f'delete me - {datetime.now().isoformat()}')
    print(f'Task created: https://to-do.office.com/tasks/id/{task["Id"]}/details')
    c.update_task(task['Id'], categories=['123', '321'])
    print('Task categories updated')
    c.add_subtask(task['Id'], 'test it')
    c.add_subtask(task['Id'], 'test it but done', is_completed=True)


if __name__ == '__main__':
    main()
