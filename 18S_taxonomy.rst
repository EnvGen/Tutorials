==============
Assigning taxonomic classification to 18S amplicon datasets
==============

This strategy was first elaborated by `Hu et al <http://journal.frontiersin.org/article/10.3389/fmicb.2016.00679/full>`_. Please cite this paper if using it.

While there are many tools available for assigning taxonomy to 16S amplicons, and some resources for fungal ITS, 
less work has been done on general eukaryotic 18S. Most 18S amplicons are also too long for reads to 
cover the whole amplicon, leaving a gap in the middle. To deal with this and other complexities, Yue Hu has
developed this strategy for optimizing accuracy and efficiency of taxonomic assignment of environmental 18S reads, 
based on the `PR2 database <http://ssu-rrna.org/>`_. 

The first step is to blast each set of reads (forward and reverse) against a curated revision of the PR2 database. 
While this database is very complete and thoroughly annotated, it includes in some cases ITS and 28S regions which
can affect the accuracy of blasting. Therefore, it is best for the purposes of this workflow to use 
`this curated subset <https://export.uppmax.uu.se/b2010008/projects-public/database/PR2_derep_3000bp.fasta>`_

STEP 1
--------
Run Blast+ for each of your datasets, requiring a standard TSV output, for instance:

  makeblastdb -in PR2_derep_3000bp.fasta	 -dbtype nucl -out PR2
  
  blastn -query fwd.fasta -db PR2 -out fwd.blast.out -evalue 0.01 -outfmt 6 -max_target_seqs 25
  
  blastn -query rev.fasta -db PR2 -out rev.blast.out -evalue 0.01 -outfmt 6 -max_target_seqs 25

STEP 2
------
Parse each of the Blast+ output files at three levels of similiarity, corresponding to species (99%), genus (97%)
and phylum (90%). This will also require `taxonomy annotations <https://export.uppmax.uu.se/b2010008/projects-public/database/PR2_derep_3000bp.tax.txt>`_
for the reference database. Example:

  python taxonomy_blast_parser.py -1 fwd.blast.out -2 rev.blast.out -id 99 -tax PR2_derep_3000bp.tax.txt > parse.99.out
  
What this step does is to consider the top 5% highest scoring hits from each read that meet the criteria for coverage and similarity, then output the last common ancestor for those which are present both in the forward and the reverse reads.
  
STEP 3
------
Combine these 3 parsed outputs into a single table that will give the most detailed information available, but fill in with lower resolution information when needed. 
The order of the input is relevant, as priority will be given to the first file named. E.g:

  python combine_taxonomy.py -i parse.99.out,parse.97.out,parse.90.out -n species,genus,phylum > taxonomy.tsv
