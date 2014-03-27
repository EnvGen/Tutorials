#!/usr/bin/perl -w

=head1 NAME

uncat_reads

=head1 SYNOPSIS

	uncat_reads [--help]  [--verbose] [--spacer=STRING] [--length=INT] --in=<fasta> [--out1=FILENAME] [--out2=FILENAME]

	 		Splits reads at a given length or separator.

	    	--help: This info.
		--spacer: sequence at which to split reads; alternatively, supply
		--length: length of forward reads; to be used instead of spacer
		--in: fasta file whose reads are to be split
		--out1, out2: name of files with each half; if not stated, out.1.fa and out.2.fa are used
	    
=head1 AUTHOR

luisa.hugerth@scilifelab.se

=cut


use warnings;
use strict;

use Bio::SeqIO;
use Getopt::Long;
use Pod::Usage;

my $fastafile;
my $spacer;
my $length;
my $out1 = "out.1.fa";
my $out2 = "out.2.fa";
my $help = 0;
my $verbose = 0;
GetOptions(
  "spacer=s" => \$spacer,
  "length=i" => \$length,
  "in=s" => \$fastafile,
  "out1=s" => \ $out1,
  "out2=s" => \ $out2,
  "help!" => \$help,
  "verbose!" => \$verbose,
);

pod2usage(0) if $help;

pod2usage(-msg => "Need an infile", -exitval => 1) unless $fastafile;
my $infile = Bio::SeqIO->new(-file=>"$fastafile", -format => "fasta") or die "Can't open $fastafile";

pod2usage(-msg => "Need a spacer or length", -exitval => 1) unless ($spacer or $length);

open OUT1, ">$out1" or die "Can't open $out1";
open OUT2, ">$out2" or die "Can't open $out2";

while (my $seq = $infile->next_seq){
	my $sequence = $seq -> seq;
	my $id = $seq -> display_id;
        if ($length>0){
	        my $seq_length=length($sequence);
                my $read1=substr($sequence, 0, $length);
                $sequence=~/^$read1(\w*)/;
                my $read2=$1;
                print OUT1 ">$id\n".$read1."\n";
                print OUT2 ">$id\n".$read2."\n";
        }
	elsif ($sequence=~/$spacer/){
		my @reads=split(/$spacer/,$sequence);
		print OUT1 ">$id\n".$reads[0]."\n";
		print OUT2 ">$id\n".$reads[1]."\n";
	}
	 else{
		print "Warning: sequence $id does not possess spacer $spacer\n";
	 }
}

close OUT1;
close OUT2;
