# trello-to-mstodo
Migrate from Trello to MS ToDo

* `import_from_trello` - create lists and tasks based on a Trello board export (JSON)
* `export_all` - export all ToDo tasks into a JSON file (backup or move away from ToDo)

## Usage

For any of the commands, you'll need the ToDo token:
* Login to https://to-do.office.com/
* Open Network inspect
* Perform any action (such as creating a new task)
* Look at network tab, locate any request to `https://substrate.office.com/todob2/api` and save the token in `Authorization` header
* Set `TODO_TOKEN` to your token
    ```
    export TODO_TOKEN=EwXas...
    ```

### Import from Trello

* Export the board from Trello
  *  Click `...` -> `Print, export and share` -> `Export JSON`
* Run the script
    ```
    ➜  ./import_from_trello.py ~/Downloads/xXxXx.json
    == Available lists ==
    * Pending
    * Defined
    * Ongoing
    * Done
    * Fail
    Select at least ONE list to import

    ➜  ./import_from_trello.py ~/Downloads/xXxXx.json -l 'Defined' -l 'Ongoing'
    Progress: 29/29
    Done
    ```
* Done
  * Preserves:
    * descriptions
    * (part of) labels
    * check lists (as subtasks)
    * adds direct link to the original card for quick reference

### Export/Backup from ToDo

> Always have an exit strategy

* Just run
  ```
  ./export.py --output BACKUP.json
  ```
* Done
  * Saves the entire task objects as they come from the GraphQL API
