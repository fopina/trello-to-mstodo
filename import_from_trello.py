#!/usr/bin/env python3

from client import Client, parser_parse, parser
from pathlib import Path
import json


def main(argv=None):
    p = parser()
    p.add_argument('trello_json', type=Path, help='JSON export from Trello dashboard')
    p.add_argument('-l', '--list', action='append', type=str, help='List to include, specify multiple times')
    args = parser_parse(argv, p=p)
    
    trello = json.loads(args.trello_json.read_text())

    if not args.list:
        print('== Available lists ==')
        for list in trello['lists']:
            print(f"* {list['name']}")
        print('Select at least ONE list to import')
        exit(1)
    
    list_set = set(x.lower() for x in args.list)
    lists = {
        l['id']: l['name']
        for l in trello['lists']
        if l['name'].lower() in list_set
    }
    cards = []
    for card in trello['cards']:
        if card['idList'] in lists:
            cards.append(card)
    
    checklists = {}
    for clist in trello['checklists']:
        _k = clist['id']
        checklists[_k] = [
            (ci['name'], ci['state'] == 'complete')
            for ci in clist['checkItems']
        ]

    c = Client(args.token)

    folders = {}
    for lk, ln in lists.items():
        f = c.create_folder(f'{ln} (from Trello)')
        folders[lk] = f

    # progress without tqdm!
    total = len(cards)
    n = 0
    for card in cards:
        f = folders[card['idList']]
        labels = [x['color'] for x in card['labels']]
        body = [f"(from {card['shortUrl']})"]
        if card['badges']['comments'] > 0:
            body.append(f"(Comments: {card['badges']['comments']})")
        body.append('')
        # mini "markdown to html" :troll:
        body.extend(card['desc'].split('\n'))

        task = c.create_task(
            f['Id'], card['name'], categories=['trello', *labels],
            body='<br/>'.join(body),
        )
        for clist in card.get('idChecklists') or []:
            for ci in checklists[clist]:
                c.add_subtask(task['Id'], ci[0], is_completed=ci[1])
        n += 1
        print(f'Progress: {n}/{total}', end='\r')
    print(f'Progress: {n}/{total}')
    print('Done')


if __name__ == '__main__':
    main()
