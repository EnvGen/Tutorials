Processing amplicons with non-overlapping reads
===============================================

This is a quick guide on how to use Usearch6 to go from fastq files all the way to a table of OTUs. More information can be found on the `Usearch project page, <http://www.drive5.com/usearch/manual/>`_. Also refer to this page for download and installation instructions. I'm going to assume in this manual that you can call Usearch simply by typing ./usearch6, but this depends on the folder where you have installed it, how you have called it and the folder you're in.

This guide is based on Illumina MiSeq reads and Usearch 6.0.x and Usearch7. Please pay attention to use the right version at each step. It might be possible to replace Usearch6.0.x with Usearch 6.1.x and it might work with 5.x.x or older. All of the steps done in Usearch7 in this manual can be done with either Fastx or Usearch6. Don't try Fastx unless you already have it in your server.

This guide is to be used if your forward and reverse reads do not overlap or if you're not sure if that's the case. If you know you have an overlap, please refer to the Usearch_overlap.pdf manual. If you're still planning your experiment, do your best to have an overlap.



*PART I: FILTERING AND MERGING*
-------------------------------

**STEP 1: Quality statistics**
	In the next step, you will have to decide how many bases you want to cut off from the end of your reads, to simultaneously preserve as many bases as possible and guarantee the quality of your reads. Therefore, in this step, you simply get some statistics on quality. For this, you can use Usearch7, Fastx, FastQC and others. If using Usearch7, the statistics are explained at length `here <http://www.drive5.com/usearch/manual/fastq_stats.html>`_. For FastQC, `check here <http://www.bioinformatics.babraham.ac.uk/projects/fastqc/>`_.

The command: 
	./usearch7 -fastq_stats <infile> -log <outfile>

Example:
	./usearch7 -fastq_stats reads_R1.fq -log reads_R1.stats


**STEP 2. Quality trimming**
	In this step, you cut off bases with low quality and trim all reads to the same length. You can use different lengths for the forward and reverse reads, but you should use the same cut-off for every sample you intend to compare. You can also choose to throw away sequences that have too low quality.

The command:
	./usearch7 -fastq_filter <infile> -fastq_trunclen <cutoff> -fastq_maxee <max error number> -fastqout <outfile>

Example:
	./usearch -fastq_filter reads_R1.fq -fastq_trunclen 280 -fastq_maxee 4 -fastqout reads_R1.trim.fq

	./usearch -fastq_filter reads_R2.fq -fastq_trunclen 250 -fastq_maxee 4 -fastqout reads_R2.trim.fq


**STEP 3: Converting to fasta**
	After the trimming is done, we no longer need the quality information.

The comand:
	grep '^@HWI' <infile> -A1 --no-group-separator | sed 's/@/>/' > <outfile>

Example:
	grep '^@HWI' reads_R1.fq -A1 --no-group-separator | sed 's/@/>/' > reads_R1.fa

If this doesn't work (are you working on a Mac?) try:
	grep '^@HWI' reads_R1.fq -A1 | grep -v '^--$' | sed 's/@/>/' > reads_R1.fa

**STEP 4: Concatenating reads**
	In this step we will concatenate the forward and reverse reads into a single artificial amplicon. You can include a separator between them, so they can be split later. Due to downstream applications, this separator can only contain the letters A, C, T, G, N. Keep in mind that the spacer you choose should be rare (long) enough that it's not likely to appear at random in your reads. However, if your forward reads have all been trimmed to the same size, you can skip the spacer and do the splitting based on length. Notice that the outfile names are defined automatically; this will be changed soon.

The command:
	perl cat_reads --spacer=<spacer_string> --revcom --file1=<forwad_reads> --file2=<reverse_reads>
or
	perl cat_reads --revcom --file1=<forward_reads> --file2=<reverse_reads>


Example
	perl cat_reads --spacer=NNNNNNNN --revcom --file1=reads_R1.fa --file2=reads_R2.fa > reads_cat.fa
or
	perl cat_reads --revcom --file1=reads_R1.fa --file2=reads_R2.fa > reads_cat.fa

*PART II: CLUSTERING*
---------------------
	
**STEP 5: File concatenation**
	In most applications, you want to compare communities from different environments, conditions etc. For this, you have to have the same OTU defined for all samples. Therefore, at this point we concatenate all files.

The command:
	cat <all_fasta_files> > <outfile>

Example:
	cat reads1.fa reads2.fa reads3.fa > all.fa

**STEP 6: Dereplication**
	Here we combine all reads that are identical into a single one, keeping track of how many copies there are of each one. This saves a lot of time down the road.

The command:
	./usearch7 -derep_fulllength <infile> -output <fasta_file> -uc <uc_file> -sizeout

Example:
	./usearch7-derep_fulllength all.fa -output all.derep.fa -uc all.derep.uc -sizeout


**STEP 7: Sorting**
	Usearch reads the fasta file in order, assigning each sequence to a cluster as it finds it. Since a sequence that has been read in many copies is most likely to be right, starting by the most frequent sequences and working your way down increases the chances the OTU found are real. We will therefore sort sequences from most frequent to least. At this point you can also throw away sequences that haven't been found a minimal amount of times. Discarding singletons will increase your precision and speed up the process, with a small lost of sensitivity. If you choose not to throw away any sequences, don't write the parameter -minsize.

The command:
	./usearch7 -sortbysize <infile> -output <outfile> -minsize <minimal cluster size>

Example:
	./usearch7 -sortbysize all.derep.fa -output all.sort.fa -minsize 2


**STEP 8: Clustering**
	Here we cluster our reads by similarity. Usearch uses average-linkage clustering, which means that it is possible that two sequences that are closer to each other than the similarity threshold can still end up in different OTU. One way to minimize this risk is to cluster at a higher similarity first, and then gradually expand these clusters.
	Since we have not removed the primer sequences, we will tell Usearch to not consider them in the clustering.
	If you're having memory problems, you can use -cluster_smallmem instead of cluster_fast. This is slightly less accurate. 

The command:
	./usearch6 -cluster_smallmem <infile> -id <identity> -uc <uc_file> -idprefix <integer> -idsuffix <integer> --centroids <fasta output>

Example:
	./usearch6 -cluster_smallmem all.sort.fa -id 0.99 -uc all.99.uc -idprefix 18 -idsuffix 18 –centroids all.99.fa -sizein -sizeout

	./usearch6 -cluster_smallmem all.99.fa -id 0.98 -uc all.98.uc -idprefix 18 -idsuffix 18 –centroids all.98.fa -sizein -sizeout

	./usearch6 -cluster_smallmem all.98.fa -id 0.97 -uc all.97.uc -idprefix 18 -idsuffix 18 –centroids all.97.fa -sizein -sizeout



**STEP 9: Renaming OTU**
	Our OTU so far have the name of the read ID of their centroid, which is simply not pleasant. Therefore, we can change their names now to OTU_1, OTU_2 etc. This script can be downloaded `here <http://drive5.com/python/>`_. You can choose any name for your OTUs, but please use OTU_ if you want to keep following this tutorial.

The command:
	python fasta_number.py <infile> <prefix> > <outfile>

Example:
	python fasta_number.py otus97.fa OTU_ > otus97num.fa

**STEP 10: Assigning reads to OTU**
	We will now look at each of our original fasta files and assign them to OTU. At this point, take the opportunity to make a directory just for your new cluster files. This is important downstream. You're also requested to say how similar your sample must be to the centroid. This must be compatible with the radius you used for clustering. For example, if you used a radius of 3%, use now a similarity of 0.97.

	In this step you may see that most reads are identified as chimera and just a small part are being recruited to OTU. That's a bug in the screen output that won't affect your data.

The command:

	./usearch7 -usearch_global <sample file> -db <numbered out file> -strand <plus/minus/both> -id <similarity to the centroid> -uc <outfile>

Example:

	./usearch7 -usearch_global reads1.merge.fa -db otus97.num.fa -strand both -id 0.97 -uc 	clusters/reads1.uc
	
Or, to run all samples without having to retype the command each time:

	SAMPLES=reads*merge.fa
	for sample in $SAMPLES; do
		./usearch7 -usearch_global $sample -db otus97.num.fa -strand both -id 0.97 -uc clusters/${file%merge.fa}uc
	done


**STEP 11: Splitting the concatenated reads**
	Now that we've assigned the reads to OTU, we have to split them again to be able to assign them a taxonomy. 

The command:
	perl uncat_reads --spacer=<spacer_string> --in=<infile> --out1=<fwd_file> --out2=<rev_file>
or	
	perl uncat_reads --length=<length> --in=<infile> --out1=<fwd_file> --out2=<rev_file>

Example:
	perl uncat_reads --spacer='NNNNNNN' --in=otus97.num.fa --out1=otus97_R1.fa --out2=otus97_R2.fa
or
	perl uncat_reads --length=220 --in=otus97.num.fa --out1=otus97_R1.fa --out2=otus97_R2.fa

*PART III: CLASSIFYING*
-----------------------

**If you're working on 18S reads:**
Please refer to the `18S taxonomy workflow <https://github.com/EnvGen/Tutorials/blob/master/18S_taxonomy.rst>`_ and then proceed to Part IV here. Otherwise, follow Steps 12 and 13 as described below.


**STEP 12: Classifying OTU**
	There are many tools for assigning taxonomy to a read. Here we use the `SINA classifier <http://www.arb-silva.de/aligner/>`_. Its online version only accepts 1000 sequences at a time. You can choose to divide your file into chunks of 1000 sequences, and then concatenate the results, or you can download and run the SINA classifier locally.


**STEP 13: Parsing taxonomy**
	The taxonomy assigned to a forward read won't always agree with the reverse read. What we do here is to take the part in which both agree.

The command:
	sina2otu --pair --sina=<sina_csv_table> --sina2=<sina_csv_table> > <outfile>

Example:
	sina2otu --pair --sina=all_R1.97.csv –sina2=all_R2.97.csv > all.97.tsv

*PART IV: OTU TABLES*
-----------------------
**STEP 14: Creating an OTU table**
	Independently of the classification method chosen above, this step will produce a table with OTUS on the lines, samples on the columns and the classification for each read and the sequence of the representative at the end of each line. You can choose to stop the taxonomy at a certain level – default is 5, or approximately class. If you want the full taxonomy, set the –depth parameter to a very large number.
	Since we have already created an artificial consensus from both our classifications, we need to inform the parser of this by choosing "tsv" as format.
	Every classification file that you want included in your OTU table should be in the same folder, and no other files should be in it. The same applies to the read assignment files (uc files), that should be in their own folder, and with nothing else there.


The command:
	perl otu_tables --depth=<INTEGER> --samples=<FOLDER> --classification=<SINA_FILE> --sequences=<FASTA> --classifier=tsv

Example:
	perl otu_tables --depth=10 --samples=clusters --classification=otus97.csv --sequences=otus97.num.fa --classifier=tsv

*PART V: BIOLOGY*
-----------------
It's beyond the scope of this tutorial to teach you how to draw biological conclusions from your OTU table. However, here are some useful links:

For visualizing your data in interactive hierarchical pie charts, use `Krona <http://sourceforge.net/p/krona/home/krona/>`_.

For information and tutorials on statistical methods for analysis of microbial ecology, take a look at `Gustame <https://sites.google.com/site/mb3gustame/home>`_.

If you believe that there are interesting OTU that are worth looking deeper into for their specific ecology, consider `oligotyping <http://merenlab.org/projects/oligotyping/>`_.
