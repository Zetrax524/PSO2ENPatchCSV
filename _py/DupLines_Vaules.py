#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import codecs
import csv
import fnmatch
import json
import multiprocessing as mp
import os
import sys

m = mp.Manager()
gD = m.dict()
cD = m.dict()
oD = m.dict()
associations = m.dict()
oL = m.list()


def check(file):
	with codecs.open(file, encoding="utf-8") as f:
		c = list(csv.reader(f, strict=True))
		for line in c:
			key = "{0}::{1}".format(os.path.basename(file), line[0])
			if key not in associations:
				continue
			oD[oL[associations[key]]] += [line[1]]


err = os.EX_OK

if len(sys.argv) < 3:
	sys.exit(os.EX_NOINPUT)

dir = sys.argv[1]
with open(sys.argv[2]) as f:
	cD = json.load(f)

fs = set()
for n, (k, v) in enumerate(cD.items()):
	oD[k] = [k]
	oL += [k]
	for i in v:
		fs.add(i.split("::")[0])
		associations[i] = n

files = [
	os.path.join(dirpath, f)
	for dirpath, dirnames, files in os.walk(dir)
	for f in fnmatch.filter(files, '*.csv')
	if f in fs
]

p = mp.Pool(mp.cpu_count())
p.map(check, files)
p.close()
p.join()

for n, (k, v) in enumerate(oD.items()):
	temp = list(set(oD[k]))
	temp.remove(k)
	oD[k] = temp

oJ = {k: v for k, v in oD.items()}

print(json.dumps(oJ, sort_keys=True))

sys.exit(err)
