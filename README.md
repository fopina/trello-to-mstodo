# trello-to-mstodo
Migrate from Trello to MS ToDo



Export from Trello

    Click "..."
    Print, export and share
    Export JSON (CSV available only for paid subscriptions)
<PICTURE OF EXPORT MENU>

Import into ToDo
Manual

this loses a lot of information lost, only adds titles

    Extract all card names using jq

get your list ID
cat ~/Downloads/boardXXX.json | jq '.lists | .[] | select(.name=="Current") | .id'
"62bxxxx"
get the cards of that list
cat ~/Downloads/boardXXX.json | jq -r '.cards | .[] | select(.idList=="62bxxxx") | .name'

    Copy all lines into "new task" - it will split into separate tasks!

Script

It would be nice to be able to add apps to our office365 and use this script "officially"

    Get the scripts from gitlab - client and import_from_trello
    Login to https://to-do.office.com/ and get your bearer token from any request after (browser network inspector or any MITM proxy)
    Run ./import_from_trello.py PATH/TO/TRELLO/EXPORT.json -l ListName -l AnotherListName -l ....
    Done - preserves descriptions, (part of) labels, check lists (as subtasks) and adds direct link to the original card for quick reference



Export OUT of ToDo

Don't pick a tool if you cannot get out of it...

Same scripts as mentioned in Trello!

    Get the scripts from gitlab - client and export_all
    Login to https://to-do.office.com/ and get your bearer token from any request after (browser network inspector or any MITM proxy)
    Run ./export.py --output BACKUP.json
    Done - saves the entire task objects as they come from the graphql API