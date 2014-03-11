#!/usr/bin/perl -w

=head1 NAME

resync

=head1 SYNOPSIS

		resync --fwd=FILE --rev=FILE --write_singles

		Takes two files and outputs files where only sequences with headers present in both files remain.

			--fwd, --rev: fasta or fastq files
		    	--write_singles: single reads will be written to a separate file
			--help: This info.

	    
=head1 AUTHOR

luisa.hugerth@scilifelab.se

=cut


use warnings;
use strict;

use Getopt::Long;
use Pod::Usage;

my $help = 0;
my $verbose = 0;
my $fwdfile;
my $revfile;
my $singles;
GetOptions(
  "help!" => \$help,
  "verbose!" => \$verbose,
  "write_singles" => \$singles,
  "fwd=s" => \$fwdfile,
  "rev=s" => \$revfile
);

pod2usage(0) if $help;

pod2usage(-msg => "Need a forward file", -exitval => 1) unless $fwdfile;
pod2usage(-msg => "Forward file must have extension fasta, fastq, fa or fq") unless ($fwdfile=~/\.f(ast)?[aq]$/);
open FWD, $fwdfile or die "Can't open $fwdfile: $!";

pod2usage(-msg => "Need a reverse file", -exitval => 1) unless $revfile;
pod2usage(-msg => "Reverse file must have extension fasta, fastq, fa or fq") unless ($revfile=~/\.f(ast)?[aq]$/);
open REV, $revfile or die "Can't open $revfile: $!";

my $max;
if ($fwdfile=~/q$/ and $revfile=~/q$/){
	$max = 5;
	print "\nFiles are fastq\n";
}
 elsif($fwdfile=~/a$/ and $revfile=~/a$/){
	$max = 3;
	print "\nFiles are fasta\n";
 }
 else{
	die "Please provide forward and reverse files of same format!";
 }

my %headers;
my $count=1;
while (my $line = <FWD>){
	if ($count == 1){
		$line=~/^(\S+)/;
		$headers{$1}=1;
		$count++;
	}
	 else{
		$count++;
		$count = 1 if ($count == $max);
	 }
}
close FWD;

$revfile=~/(\S+)\.\w+$/;
my $root=$1;
if ($max==5){
	open REV_OUT, ">$root.sync.fastq";
	open SINGLES, ">$root.singles.fastq" if $singles;
}
else{
	open REV_OUT, ">$root.sync.fasta";
        open SINGLES, ">$root.singles.fasta" if $singles;
}

$count=1;
my $paired = 'no';
while (my $line = <REV>){
	if ($count == 1){
		$line=~/^(\S+)/;
		if (exists ($headers{$1})){
			delete $headers{$1};
			$paired = 'yes';
			print REV_OUT $line;
		}
		 elsif($singles){
			print SINGLES $line;
		 }
		$count++;
	}
	 else{
		print REV_OUT $line if ($paired eq 'yes');
		print SINGLES $line if ($paired eq 'no' and $singles);
		$count++;
		if ($count == $max){
			$count = 1;		
			$paired= 'no';
		}
	 }
}

close REV;
close REV_OUT;

open FWD, $fwdfile;
$fwdfile=~/(\S+)\.\w+$/;
$root=$1;
if ($max==5){
        open FWD_OUT, ">$root.sync.fastq";
}   
else{
        open FWD_OUT, ">$root.sync.fasta";
}

while (my $line = <FWD>){
	if ($count == 1){
		$line=~/^(\S+)/;
		if (!exists ($headers{$1})){
			$paired = 'yes';
			print FWD_OUT $line;
		}
		 elsif($singles){
			print SINGLES $line;
		 }
		$count++;
	}
	 else{
		print FWD_OUT $line if ($paired eq 'yes');
		print SINGLES $line if ($paired eq 'no' and $singles);
		$count++;
		if ($count == $max){
			$count = 1;		
			$paired = 'no';
		}
	 }
}

close FWD;
close FWD_OUT;
close SINGLES if $singles;
