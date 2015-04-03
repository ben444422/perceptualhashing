from util import DocumentSet
import json
import sys

out_file = sys.argv[2]

ds = DocumentSet()
new_len = 100

data = []
for title in ds.documents:
	if new_len == 0:
		break
	data.append({
		"title": title,
		"body" : ds.documents[title]
		})
	new_len -= 1





with open(out_file, 'w') as outfile:
    json.dump(data, outfile)