#!/usr/bin/perl -w

=head1 NAME

cat_reads

=head1 SYNOPSIS

	cat_reads [--help]  [--verbose] [--spacer=STRING] [--revcom] [--print-single] --file1=<fasta> --file2=<fasta>

	 		Concatenates reads with the same ID.
			Reads only present in one of the files will be outputted separately.

	    --help: This info.
		--spacer: an optional sequence to be added between reads
		--revcom: the sequences in file2 should be reverse complemented before concatenation
		--print_single: write out sequences that don't have a mate-pair into separate files
							these will be named <file1name>_only.fa and  <file2name>_only.fa
		--file1, file2: fasta files with headers in common
	    
=head1 AUTHOR

luisa.hugerth@scilifelab.se

=cut


use warnings;
use strict;

use Bio::SeqIO;
use Bio::Perl;
use Getopt::Long;
use Pod::Usage;

my $file1;
my $file2;
my $revcom;
my $spacer = "";
my $singles;
my $help = 0;
my $verbose = 0;
GetOptions(
  "spacer=s" => \$spacer,
  "file1=s" => \$file1,
  "file2=s" => \$file2,
  "revcom!" => \$revcom,
  "help!" => \$help,
  "verbose!" => \$verbose
);

pod2usage(0) if $help;

pod2usage(-msg => "Need two fasta files", -exitval => 1) unless $file1 and $file2;
my $fwd_file = Bio::SeqIO->new(-file=>"$file1", -format => "fasta") or die "Can't open $file1";
my $rev_file = Bio::SeqIO->new(-file=>"$file2", -format => "fasta") or die "Can't open $file2";

my %fwd_reads;
while (my $seq = $fwd_file->next_seq){
	my $id = $seq -> display_id;
	my $read = $seq -> seq;
	$fwd_reads{$id} = $read;
}

$file1=~/^(\S+)\.fa/;
my $name_fwd=$1;
$file2=~/^(\S+).fa/;
my $name_rev=$1;
my $fwdout = $name_fwd . "_only.fa";
my $revout = $name_rev . "_only.fa";

if ($singles){
	open FWD, ">$fwdout" or die "Can't open outfile $fwdout";
	open REV, ">$revout" or die "Can't open outfile $revout";
}

while (my $seq = $rev_file->next_seq){
	my $id = $seq -> display_id;
	my $rev_read = $seq -> seq;
	$rev_read = reverse_complement_as_string($rev_read) if $revcom;
	if (exists $fwd_reads{$id}){
		print ">$id\n".$fwd_reads{$id}.$spacer.$rev_read."\n";
		delete ($fwd_reads{$id});
	}
	 elsif($singles){
		print REV ">$id\n$rev_read\n";
	 }
}

if($singles){
	while (my ($id, $read) = each(%fwd_reads)){
		print FWD ">$id\n$read\n";
	}
}

close BOTH;
if($singles){
	close FWD;
	close REV;
}
