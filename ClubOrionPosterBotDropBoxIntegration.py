import argparse
import contextlib
import datetime
import os
import six
import sys
import time
import unicodedata


import dropbox

def upload_to_dropbox(DBOXTOKEN):
    parser = argparse.ArgumentParser(description='Upload the LobbyPosters-Orion-1-Export.png file to Dropbox')
    parser.add_argument('folder', nargs='?', default='Orion Poster Bot', help='Folder name in your Dropbox')
    parser.add_argument('rootdir', nargs='?', default='I:\ClubOrionGithubWebsite\Club-Orion', help='Local directory to upload')
    parser.add_argument('--token', default=DBOXTOKEN,help='Access token ''(see https://www.dropbox.com/developers/apps)')
    parser.add_argument('--yes', '-y', action='store_true', help='Answer yes to all questions')
    parser.add_argument('--no', '-n', action='store_true',help='Answer no to all questions')
    parser.add_argument('--default', '-d', action='store_true', help='Take default answer on all questions')
    """Main program.
    Parse command line, then iterate over files and directories under
    rootdir and upload all files.  Skips some temporary files and
    directories, and avoids duplicate uploads by comparing size and
    mtime with the server.
    """

    fullname = "LobbyPosters-Orion-1-Export.png"
    args = parser.parse_args()

    if sum([bool(b) for b in (args.yes, args.no, args.default)]) > 1:
        print('At most one of --yes, --no, --default is allowed')
        sys.exit(2)
    if not args.token:
        print('--token is mandatory')
        sys.exit(2)

    folder = args.folder
    rootdir = os.path.expanduser(args.rootdir)
    print('Dropbox folder name:', folder)
    print('Local directory:', rootdir)
    if not os.path.exists(rootdir):
        print(rootdir, 'does not exist on your filesystem')
        sys.exit(1)
    elif not os.path.isdir(rootdir):
        print(rootdir, 'is not a folder on your filesystem')
        sys.exit(1)

    dbx = dropbox.Dropbox(args.token)
    upload(dbx, fullname,folder)

    dbx.close()

def upload(dbx, fullname,folder, overwrite=False):
    path = "Dropbox/Apps/Orion Poster Bot"
    path = '/%s/%s/%s' % ("Apps",folder, fullname)
    while '//' in path:
        path = path.replace('//', '/')

    mode = (dropbox.files.WriteMode.overwrite
            if overwrite
            else dropbox.files.WriteMode.add)
    mtime = os.path.getmtime(fullname)
    with open(fullname, 'rb') as f:
        data = f.read()
    with stopwatch('upload %d bytes' % len(data)):
        try:
            res = dbx.files_upload(
                data, path, mode,
                client_modified=datetime.datetime(*time.gmtime(mtime)[:6]),
                mute=True)
        except dropbox.exceptions.ApiError as err:
            print('*** API error', err)
            return None
    print('uploaded as', res.name.encode('utf8'))
    return res

def yesno(message, default, args):
    """Handy helper function to ask a yes/no question.
    Command line arguments --yes or --no force the answer;
    --default to force the default answer.
    Otherwise a blank line returns the default, and answering
    y/yes or n/no returns True or False.
    Retry on unrecognized answer.
    Special answers:
    - q or quit exits the program
    - p or pdb invokes the debugger
    """
    if args.default:
        print(message + '? [auto]', 'Y' if default else 'N')
        return default
    if args.yes:
        print(message + '? [auto] YES')
        return True
    if args.no:
        print(message + '? [auto] NO')
        return False
    if default:
        message += '? [Y/n] '
    else:
        message += '? [N/y] '
    while True:
        answer = input(message).strip().lower()
        if not answer:
            return default
        if answer in ('y', 'yes'):
            return True
        if answer in ('n', 'no'):
            return False
        if answer in ('q', 'quit'):
            print('Exit')
            raise SystemExit(0)
        if answer in ('p', 'pdb'):
            import pdb
            pdb.set_trace()
        print('Please answer YES or NO.')

@contextlib.contextmanager
def stopwatch(message):
    """Context manager to print how long a block of code took."""
    t0 = time.time()
    try:
        yield
    finally:
        t1 = time.time()
        print('Total elapsed time for %s: %.3f' % (message, t1 - t0))    

    return