import os
import frontmatter
import markdown
import json
from google.cloud import firestore

# Stolen from firebase docs, just wipes all the slides out before our
# new deploy
def delete_collection(coll_ref, batch_size=10):
    docs = coll_ref.limit(batch_size).stream()
    deleted = 0

    for doc in docs:
        print(u'-> Deleting doc {} => {}'.format(doc.id, doc.to_dict()))
        doc.reference.delete()
        deleted = deleted + 1

    if deleted >= batch_size:
        return delete_collection(coll_ref, batch_size)

config_file = './config.json'
config_collection = u'config'
slide_collection = u'slides'
slide_dir = './posts'

files = os.listdir(slide_dir)

slides = []

# Load them all into memory
for file in files:
    post = frontmatter.load('{}/{}'.format(slide_dir, file))
    slides.append(post)

# Sort into the correct order
slides = sorted(slides, key=lambda x: x['order'])

# Setup the configuration
db = firestore.Client().collection(config_collection)
print('[!] Removing existing config')
delete_collection(db)
with open(config_file) as config:
    doc_ref = db.document('main')
    doc_ref.set(json.load(config))

# Now deal with the slides
db = firestore.Client().collection(slide_collection)
print('[!] Removing existing slides')
delete_collection(db)
print('[!] Adding new slides')
for slide in slides:
    document = {
        'content': markdown.markdown(slide.content),
    }
    # Add any extra items to the document, like background etc
    for key in slide.keys():
        document[key] = slide[key]
    print('-> Adding doc {}'.format(document))
    doc_ref = db.document("slide-{}".format(slide['order']))
    doc_ref.set(document)
