import argparse
import datetime
import sys

from supporters.settings import Settings
from supporters.database import Database
import supporters.tasks_common as task_action
from supporters.taskitem import TaskItem


# TODO: parser.add_argument("-tom", "--tomorrow", help="tomorrow")


def initialization(breefkase_dir):
    database = Database(breefkase_dir, 'tasks')
    if not database.collection_path:
        print("No database directory in settings")
    retries = 5
    while not database.collection_path:
        retries -= 1
        if not retries:
            sys.exit("Database path could not be established")
        breefkase_dir = input("Enter full path:")
        if not len(breefkase_dir):
            continue
        database = Database(breefkase_dir, 'tasks')
    return database


settings = Settings()
db = initialization(settings.breefkase_dir)


class bcolors:
    """Colors"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


"""Common functions"""


def print_doc(doc):
    print(bcolors.OKCYAN, "-" * 16, bcolors.ENDC)
    printable = {
        "ID": doc["_id"],
        "Status": doc["status"],
        "Title": doc["title"],
    }
    if doc.get("end", None):
        printable["Ended"] = doc["end"]
    else:
        printable["Due"] = doc["due"]
    print(bcolors.WARNING)
    for key, value in printable.items():
        print(f"""{key}
        {value}""")
    print(bcolors.ENDC)


def print_docs(docs):
    for docitem in docs:
        print_doc(docitem["doc"])


def today(*args):
    docs = db.fetchall()
    docs_filtered = task_action.filter_today(docs)
    print_docs(docs_filtered)
    print(8 * "*")
    print(f"Of {len(docs)} tasks, {len(docs_filtered)} are due")


def add(*args):
    print(10 * "-")
    title = input('Task text:')
    entry = {
        "_id": "new",
        "title": title,
        "due": datetime.datetime.now().isoformat(),
        "priority": None,
    }
    result = task_action.save_task(entry, db)
    if result:
        print("Inserted: ", title)


def cancel(args):
    if not args.id:
        print("No id given. Use --id")
        return
    task = TaskItem(args.id, db)
    task.cancel()
    print(f"Task {args.id} marked as cancelled")


def done(args):
    if not args.id:
        print("No id given. Use --id")
        return
    task = TaskItem(args.id, db)
    task.done()
    print(f"Task {args.id} marked as done")


def view(args):
    try:
        docid = args.id
        task = TaskItem(docid, db)
        print_doc(task.doc)
    except KeyError:
        print(f"Could not find id {args.id}")


def delete(args):
    if not args.id:
        print("No id given. Use --id")
        return
    try:
        docid = args.id
        task = TaskItem(docid, db)
        db.delete(task.docitem["filepath"])
    except KeyError:
        print(f"Could not find id {args.id}")


def archive(args):
    print(f"Archiving...")
    # TODO: Implement for cancelled status, the same as for done
    if args.done:
        print("Marking ")
        docs = db.fetchall()
        for d in docs:
            task = TaskItem(d["doc"]["_id"], db)
            status = task.doc.get("status", None)
            archived = task.doc.get("archived", None)
            if status == "done" and not archived:
                print(task.doc)
                task.archive()
    db.archive()


def unarchive(args):
    db.unarchive()


"""
Parser
"""
parser = argparse.ArgumentParser(
    prog='breefkase CLI Interface',
    usage='%(prog)s [options] path. -h for help',
    description='Interface for interacting with a breefkase directory',
    epilog='Enjoy the program! :)')
parser.add_argument("-m", "--menu", help="CLI-interface w/menu")
subparsers = parser.add_subparsers()
parser_today = subparsers.add_parser('today',
                                     aliases=['tod'],
                                     help='Today and overdue tasks')
parser_today.set_defaults(func=today)
parser_add = subparsers.add_parser('add',
                                   aliases=['new', 'create'],
                                   help='Add new task')
parser_add.set_defaults(func=add)
# TODO: Ineffective parsing. Combine cancel and done
parser_cancel = subparsers.add_parser('cancel', help='Mark task as cancelled. Takes --id argument')
parser_cancel.add_argument('-i', '--id', default=None, help="Task ID")
parser_cancel.set_defaults(func=cancel)

parser_done = subparsers.add_parser('done', help='Mark task as done. Takes --id argument')
parser_done.add_argument('-i', '--id', default=None, help="Task ID")
parser_done.set_defaults(func=done)

parser_view = subparsers.add_parser('view', help='View task. Takes --id argument')
parser_view.add_argument('-i', '--id', default=None, help="Task ID")
parser_view.set_defaults(func=view)

parser_delete = subparsers.add_parser('delete', help='Delete task. Takes --id argument')
parser_delete.add_argument('-i', '--id', default=None, help="Task ID")
parser_delete.set_defaults(func=delete)

parser_archive = subparsers.add_parser('archive', help='Archives all tasks having archived:true')
parser_archive.add_argument('--done', default=False, action="store_true",
                            help="Includes done & cancelled tasks, and marks them as archived")
parser_archive.set_defaults(func=archive)

parser_unarchive = subparsers.add_parser('unarchive', help='Unarchives all tasks from archive')
parser_unarchive.set_defaults(func=unarchive)


def menu():
    print("Work in progress. Tasks CLI Menu")


def main():
    if len(sys.argv) <= 1:
        sys.argv.append('--help')
    print("Running Tasks CLI Argument Parser")
    print(16 * ">")
    args = parser.parse_args()
    args.func(args)
