#!/usr/bin/perl -w

=head1 NAME

uc_tables

=head1 SYNOPSIS

	uc_tables [--help] [--verbose] --fine=uc_file --coarse=uc_file

	  Takes 2 Usearch UC files done in order and increasing coarseness.
	  It keeps track of which sequences in the first, finer file are in each centroid
		and reasigns them to the corresponding centroind in the second, coarser file.
	  The output format is as a table
			centroid *
			sequence centroid

	    --help: This info.
		--fine: UC file with a finer clustering (e.g. 99%)
		--coarse: UC file done clustering the output fasta file from the
			finer clustering at a coarser level (e.g. 97%)

=head1 AUTHOR

luisa.hugerth@scilifelab.se

=cut

use warnings;
use strict;

use Bio::SeqIO;
use Getopt::Long;
use Pod::Usage;

my $help = 0;
my $verbose = 0;
my $fine;
my $coarse;
GetOptions(
  "help!" => \$help,
  "verbose!" => \$verbose,
  "fine=s" => \$fine,
  "coarse=s" => \$coarse,
);

pod2usage(0) if $help;

pod2usage(-msg => "Need a fine file", -exitval => 1) unless $fine;
open FINE, $fine or die "Can't open $fine: $!";

pod2usage(-msg => "Need a coarse file", -exitval => 1) unless $coarse;
open COARSE, $coarse or die "Can't open $coarse: $!";

my %clusters;
while (my $line = <FINE>){
	if ($line=~/^[SH]/){
		$line=~/(\S+)\t(\S+)$/;
		my $id=$1;
		my $centroid=$2;
		$id=~/^(\S+);size=\d+;$/;
		$id=$1;
#		print "$id => $centroid\n";
		if ($centroid ne '*'){
			if ($centroid=~/;/){
				$centroid=~/^(\S+);size=\d+;$/;
				$centroid=$1;
			}
			push (@{$clusters{$centroid}}, $id);
#			print "Cluster $centroid stored id ".$id."\n";
		}
#		print $clusters{$1};
	}
}
close FINE;

while (my $line = <COARSE>){
	if ($line=~/^[SH]/){
		$line=~/(\S+)\t(\S+)$/;
		my $first = $1;
		my $centroid = $2;
		if ($first=~/;/){
			$first=~/^(\S+);size=\d+;$/;
			$first=$1;
		}
		if ($centroid ne '*'){
			if ($centroid=~/;/){
				$centroid=~/^(\S+);size=\d+;$/;
				$centroid=$1;
			}
		}
        print "S\t$first\t$centroid\n";	
		if (exists ($clusters{$first})){
#print "there are layers under the 1st\n";
			my @aux_array = $clusters{$first};
			foreach my $index (@aux_array){
				foreach (@{$index} ){
					print "S\t$_\t$centroid\n";
				}
			}
		}
		 elsif (exists $clusters{$centroid}){
#print "There is more under this centroid\n";
			my @aux_array = $clusters{$centroid};
			foreach my $index (@aux_array){
				foreach (@{$index} ){
					print "S\t$_\t$centroid\n";
				}
			}			
		 }				
	}
}
close COARSE;
