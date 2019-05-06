#!/usr/bin/env python

"""Taxonomy_blast_parser.py: finds the best taxonomic classification from 2 blast files.

From tab-separated blast files corresponding to fwd and rev reads,
the 5% top HSP making cutoffs for evalue, coverage and identity 
in both files are used for LCA determination"""

from __future__ import division
from collections import defaultdict
from os.path import commonprefix
import argparse
import csv
import math
import re


__author__ = "Yue O Hu and Luisa W Hugerth"
__email__ = "luisa.hugerth@scilifelab.se"


def blast_parser(blastfile, maxeval, mincov, minID, length):
	#Save all blast hits that make the cutoff in similarity and ID
	scores = defaultdict(dict)
	with open(blastfile) as csvfile:
		reader = csv.reader(csvfile, delimiter="\t")
		for row in reader:
		##queryId, subjectId, percIdentity, alnLength, mismatchCount, gapOpenCount, queryStart, queryEnd, subjectStart, subjectEnd, eVal, bitScore
			if len(row) > 0:
				if row[0][0] != "#":
					query = row[0]
					hit = row[1]
					percid = float(row[2])
					hlength = int(row[7]) - int(row[6])
					evalue = float(row[10])
					cov = 100*hlength/length
					score = float(row[11])
					#print query + "\t" + hit + "\t" + str(evalue) + "\t" + str(percid) +"\t" + str(cov)
					if (evalue <= maxeval and percid >= minID and cov >= mincov):
						#print "Made the cutoff: " + query
						scores[query][hit] = score
	return scores

		
def parse_taxonomy(taxfile):
	tax = defaultdict(list)
	with open(taxfile) as csvfile:
		reader = csv.reader(csvfile, delimiter="\t")
		for row in reader:
		#AB353770.1.1740_U	Eukaryota;Alveolata;Dinophyta;Dinophyceae;Dinophyceae_X;Dinophyceae_XX;Peridiniopsis;Peridiniopsis+kevei;
			tax[row[0]] = row[1]
	return tax


def lca(scores1, scores2, tax):
	classdict = dict()
	for query, hit in scores1.items():
		scr1 = set(hit.keys())
		scr2 = set(scores2[query].keys())
		#find the common hits of both dictionaries
		common = scr1.intersection(scr2)
		commonscores=dict()
		topscore = 0
		for goodhit in common:
			score = hit[goodhit] + scores2[query][goodhit]
			commonscores[goodhit] = score
			if score > topscore:
				topscore = score
		#remove from common all the scores that aren't at least 95% of topscore
		minscore = 0.95*topscore
		topscores = commonscores.copy()
		for goodhit in commonscores:
			if commonscores[goodhit] < minscore:
				del topscores[goodhit]
		#get the LCA for these
		classify = ''
		for tophit in topscores:
			if classify == '' and tophit in tax:
				classify = str(tax[tophit])
			else:
				#print "And the common pref is " + commonprefix([classify, str(tax[tophit])])
				classify = commonprefix([classify, str(tax[tophit])])
		if classify == '' or classify == '[]':
			classify = 'Unclassified;'
		#take longest substr ending in ;
		meaningful = re.match(".+;", classify)
		classify = meaningful.group()
		classdict[query] = classify
	return classdict

def print_class(classified):
	print("Query\tTaxonomy")
	for query, tax in classified.items():
		print(query + "\t" + str(tax))
	
def main(blast1, blast2, evalue, coverage, identity, taxonomy, len1, len2):
##### METHOD #######
#1 filter the blast result with cutoffs 90, 97 or 99 and aligned length 90% 
#2 find the blast matches in both FWD and REV qualified items
#3 sum the score of those matches and rank them
#4 take blast annotations that have >=95% of the best bitscore; Last Common Ancestor for the classification
	#parse taxonomy
	tax = parse_taxonomy(taxonomy)
	#parse blast result for each file at user cutoff
	scores1 = blast_parser(blast1, evalue, coverage, identity, len1)
	scores2 = blast_parser(blast2, evalue, coverage, identity, len2)
	#find the results common for forward and reverse, rank them and get the LCA of the top 5%
	classified = lca(scores1, scores2, tax)
	#print out the result
	print_class(classified)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Takes 2 blast output files and a taxonomy table and returns best taxonomic classification')
	parser.add_argument('-1', '--blast1', help='Blast output for forward reads')
	parser.add_argument('-2', '--blast2', help='Blast output for reverse reads')
	parser.add_argument('-e', '--evalue', nargs='?', default=1E-5, type=float, help='Maximal evalue to consider blast match. Default: %(default)f')
	parser.add_argument('-c', '--coverage', nargs='?', default=90.0, type=float, help='Minimal coverage of blast query to consider match. Default: %(default)d per cent')
	parser.add_argument('-id', '--identity', nargs='?', default=99.0, type=float, help='Maximal residue identity of interest to consider a match. Default: %(default)d per cent')
	parser.add_argument('-tax', '--taxonomy', help='Annotated taxonomy for last common ancestor inference')
	parser.add_argument('-l1', '--length1', type=int, help="Length of reads from blast1")
	parser.add_argument('-l2', '--length2', type=int, help="Length of reads from blast2")
	args = parser.parse_args()
	
	main(args.blast1, args.blast2, args.evalue, args.coverage, args.identity, args.taxonomy, args.length1, args.length2)

