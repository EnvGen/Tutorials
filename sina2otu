#!/usr/bin/perl -w

=head1 NAME

sina2otu

=head1 SYNOPSIS

	sina2otu [--help] [--verbose] [--pair] [--number] [--ol|--cl] --sina=<sina_csv_table> [--sina2=<sina_csv_table>] [--by-taxon]

		Takes 2 tables: one associationg read ID and cluster size, one SINA classification table.
		Outputs a table with phylogeny and read counts.	
		If pair is activated, it will find the lowest taxonomic consensus between forward and reverse reads.		

			--help: This info.
			--pair: two sina files with matching sequence ID will be given
			--number: replace the headers in sina files for OTU_1, OTU_2....
			--sina, sina2: standard sina classification output
			--by-taxon: output counts for each taxon.
			--cl: command-line sina with standard output was used [default]
			--ol: online sina was used and the result downloaded

		
=head1 AUTHOR

luisa.hugerth@scilifelab.se

=cut

use warnings;
use strict;

use Getopt::Long;
use Pod::Usage;

my $help = 0;
my $verbose = 0;
my $sinafile;
my $othersina;
my $number;
my $pair = 0;
my $by_taxon = 0;
my $online = 0;
my $command;
GetOptions(
  "help!" => \$help,
  "verbose!" => \$verbose,
  "sina=s" => \$sinafile,
  "sina2=s" => \$othersina,
  "pair!" => \$pair,
  "number!" => \$number,
  "by-taxon!" => \$by_taxon,
  "ol!" => \$online,
  "cl!" => \$command
);

pod2usage(0) if $help;

pod2usage(-msg => "Please provide at least one sina file", -exitval => 1) unless $sinafile;
pod2usage(-msg => "Pair usage requires 2 sina files", -exitval => 1) if ($pair and not $othersina);
$command = 0 if ($online);
open SINA, $sinafile or die "Can't open $sinafile: $!";
(open SINA2, $othersina or die "Can't open $othersina: $!") if $pair;


my %phylo;
my $counter=1;
while (my $line = <SINA>){
	unless ($line=~/^"job_id"/ or $line=~/^name/){
		chomp $line;
		my ($tax, $id);
		my @fields;
		if ($command){
			@fields = split(',', $line);
			$id =  $fields[0];
			$tax = $fields[-5];
		}
		 elsif ($online){
			@fields = split(',', $line);
			$id =  $fields[2];
			$tax = $fields[-1];
		 }
		$tax =~ s/\r//g;
		$tax =~ s/ /_/g;
		$tax = substr ($tax, 1, length($tax)) if ($tax=~/^;/);
		unless ($pair){
			my @taxa = split (';', $tax);
			my $short_tax = $taxa[-1];
			$id = "OTU_$counter" if $number;
			print "$id\t$short_tax\t$tax\n";
			$counter++;
		}
		 else{
			$phylo{$id}=$tax;
		 }	
	}
}
close SINA;

my %tax_counter;
$counter = 1;
if ($pair){
	while (my $line = <SINA2>){
		unless ($line=~/^"job_id"/ or $line=~/^name/){
			chomp $line;
			my ($tax2, $id);
			my @fields;
			if ($command){
				@fields = split(',', $line);
				$id =  $fields[0];
				$tax2 = $fields[-5];
			}
			 elsif ($online){
				@fields = split(',', $line);
				$id =  $fields[2];
				$tax2 = $fields[-1];
			 }
			$tax2 =~ s/\r//g;
			$tax2 =~ s/ /_/g;
			$tax2 = substr ($tax2, 1, length($tax2)) if ($tax2=~/^;/);
			my $tax=$tax2;
			my @taxa2 = split (';', $tax2);
			my $short_tax;
			my @consensus;
			if (exists $phylo{$id}){
				my $tax1 = $phylo{$id};
				my @taxa1 = split (';', $tax1);
				my $field_count=0;
				for my $tax (@taxa1){
					if (exists $taxa2[$field_count]){
						if ($tax eq $taxa2[$field_count]){
							push (@consensus, $tax);
						}
						 elsif ($field_count == 0){
							push (@consensus, "Unclassified");
						 }
					}
					 else{
						@consensus=@taxa1;
					 }
					$field_count++;
				}
			} 
			 else{
				@consensus=@taxa2;
			 }
			$tax = join (';',@consensus);
			if ($tax !~ ";"){
				$short_tax = $tax;
			}
			 elsif ($command){
	            $short_tax = $consensus[-1];
			 }
			 elsif ($online){
				$short_tax = $consensus[-2];
			 }
			unless ($by_taxon){
				$id = "OTU_$counter" if $number;
				print "$id\t$short_tax\t$tax\n";
				$counter++;
			}
			 else{
				$tax_counter{$tax}+=1;
			 }
		}
	}
}
close SINA2 if $pair;

if ($by_taxon){
	while (my ($taxon, $count) = each %tax_counter){
		print "$taxon\t$count\n";
	}
}
