#!/usr/bin/env python

"""Combine_classifications.py: fills in taxonomic classification from separate tsv.

"""

from collections import defaultdict
import argparse
import csv
import re


__author__ = "Yue O Hu and Luisa W Hugerth"
__email__ = "luisa.hugerth@scilifelab.se"

def parsetax(taxdict, leveldict, taxfile, level, depth):
	with open(taxfile) as csvfile:
		reader = csv.reader(csvfile, delimiter="\t")
		next (reader, None)
		for row in reader:
			query = row[0]
			tax = row[1]
			taxlist = tax.split(";")
			taxlist = taxlist[0:int(depth)]
			tax = ";".join(taxlist)
			#print tax
			if re.search(";$", tax):
				#print "Ended in ;"
				useful = re.match("(.+?);+$", tax)
				tax = useful.group()
			else:
				tax = tax + ";"
			if query not in taxdict or taxdict[query] == "Unclassified;":
				taxdict[query] = tax
				leveldict[query] = level
	return taxdict, leveldict


def main(infiles, names, depths):
	filelist = infiles.split(",")
	namelist = names.split(",")
	depthlist = depths.split(",")
	count = 0
	taxdict = dict()
	leveldict = dict()
	for infile in filelist:
		taxdict, leveldict = parsetax(taxdict, leveldict, infile, namelist[count], depthlist[count])
		count += 1
	print("Seq_id\tSim_level\tTaxonomy")
	for query, tax in taxdict.items():
		if (tax == 'Unclassified;'):
			print(query + "\tUnclassified\tUnclassified;")
		else:
			print(query + "\t" + leveldict[query] + "\t" + tax)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Combines taxonomic assignment at different stringency levels')
	parser.add_argument('-i', '--infiles', help='Paths to relevant tsv taxonomies (outputs of taxonomy_blast_parser.py) in priority order,\
													\ separated by ","')
	parser.add_argument('-n', '--names', help='Short names for the taxonomies, in the same order, separated by ","')
	parser.add_argument('-d', '--depths', help='Maximum depth to consider for each blast result, starging at 0, separated by ","')
	args = parser.parse_args()

	main(args.infiles, args.names, args.depths)

