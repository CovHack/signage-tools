import os
import argparse
from google.cloud import firestore
import datetime

def delete_collection(coll_ref, batch_size=10):
    docs = coll_ref.limit(batch_size).stream()
    deleted = 0

    for doc in docs:
        print(u'-> Deleting doc {} => {}'.format(doc.id, doc.to_dict()))
        doc.reference.delete()
        deleted = deleted + 1

    if deleted >= batch_size:
        return delete_collection(coll_ref, batch_size)

content = "Hello World"

parser = argparse.ArgumentParser(description='Send Notifications to signage')
parser.add_argument('--collection',
                    dest='collection',
                    default='notifications'
                )
parser.add_argument('--expire',
                    dest='diff',
                    type=int,
                    default=1
                )
parser.add_argument('--clear', action='store_true')
parser.add_argument('message',
                    type=str,
                    default='',
                    nargs='?')
args = parser.parse_args()

db = firestore.Client().collection(args.collection)
if args.clear:
    print('[!] Clearing notifications')
    delete_collection(db)

if args.message != '':
    doc_ref = db.document(datetime.datetime.now().isoformat())
    doc_ref.set(
        {
            'content': args.message,
            'date': datetime.datetime.now().isoformat(),
            'expire': (datetime.datetime.now()
                       + datetime.timedelta(minutes=args.diff)).isoformat()
        }
    )

