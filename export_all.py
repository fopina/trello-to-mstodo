#!/usr/bin/env python3

from client import Client, parser_parse, parser
from pathlib import Path
import json


def main(argv=None):
    p = parser()
    p.add_argument('--completed', action='store_true', help='Include completed tasks')
    p.add_argument('-o', '--output', type=Path, help='JSON file to create with all the tasks')
    args = parser_parse(argv, p=p)
    c = Client(args.token)
    folders = list(c.list_folders())
    tasks = []

    total = len(folders)
    n = 0
    for f in folders:
        if args.output:
            print(f'Lists done: {n}/{total}', end='\r')
        else:
            print(f'== Folder {f["Name"]}')
        for t in c.list_tasks(f["Id"]):
            if not args.completed and t['CompletedByUser']:
                continue
            tasks.append(t)
            if not args.output:
                print(t['Subject'])
        n += 1
    if args.output:
        print(f'Lists done: {n}/{total}')

    if args.output:
        args.output.write_text(json.dumps({'folders': folders, 'tasks': tasks}))


if __name__ == '__main__':
    main()
