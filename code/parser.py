import sys
from bs4 import BeautifulSoup, Comment, Tag
import fnmatch
import os
import json
directory = sys.argv[1]
out_file = sys.argv[2]

remove_strings = ["from wikipedia, the free encyclopedia"]

def find_files(directory, pattern):
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                yield (basename, open(filename))


def parse_files(files):
	count = 0
	for f in files:
		file_name = f[0]
		file_handle = f[1]

		print "Processing file " + str(count) + ": " + file_name
		count += 1
		soup = BeautifulSoup(file_handle)
		
		# skip if the wikipedia page is disambiguous (many topics fall under the same name)
		if soup.find(id="disambig") != None:
			print "Skipping due to disambiguity"
			continue

		content = soup.find(id="bodyContent")

		# skip if it can't be parsed
		if content == None:
			print "Skipping because can't be parsed"
			continue

		clean(content)
		content_text = content.getText()

		content_text = " ".join([word for word in content_text.lower().split()])
		for s in remove_strings:
			content_text = content_text.replace(s, "")
		topic = file_name.replace(".html", "")
		yield (file_name, topic, content_text)
		
def clean(content):
	for e in content.findAll("div", { "class" : ["metadata", "printfooter", "references-small"]}):
		e.extract()
	for e in content.findAll("div", { "id" : ["catlinks"]}):
		e.extract()
	for e in content.findAll("script"):
		e.extract()
	for e in content(text=lambda text : isinstance(text, Comment)):
		e.extract()


files = find_files(directory,'*.html')
data = []
i = 0
for f in parse_files(files):
	data.append({
		"title": f[1],
		"body" : f[2]
		})
	i += 1
print i

with open(out_file, 'w') as outfile:
    json.dump(data, outfile)


# data_new = json.loads(js)
# print data_new
# 	# print "================================================================"
# 	# print f[1] + "\n\n"
# 	# print f[2]
# 	# print "================================================================"