#!/usr/bin/perl
# -*- cperl -*-
#!/usr/bin/perl -CSD

require 5.0;
use strict;
use FindBin;
use Getopt::Std;


use lib "/home/miewkeen/unsw/svn/citations/ESuRFr/refExt2";

# Dependencies
use File::Spec;
use File::Basename;

use refExt2::PreProcess;
use encoding "utf-8";
use JSON;


sub usage
{
    print "preprocess_refext2.pl\n";
    print "Usage: perl preprocess_refext2.pl <textfile>\n";
    exit 1;
}

# main program
my $textfile = $ARGV[0];
my $argc=scalar(@ARGV);
#print "start\n";
if ($argc != 1)
{
    usage();
}

my @pos_array = (); 
# Reference text, boby text, and normalize body text
my ($rcite_text, $rnorm_body_text, $rbody_text) = undef;
# Reference to an array of single reference
my $rraw_citations = undef;
    
if (! open(IN, "<:utf8", $textfile)) 
{ 
    print ("Could not open text file " . $textfile . ": " . $! . "\n"); 
    exit 1;
}
my $text = do { local $/; <IN> };
close IN;
        

($rcite_text, $rnorm_body_text, $rbody_text) = refExt2::PreProcess::FindCitationText(\$text, \@pos_array);


# Extract citations from citation text
$rraw_citations	= refExt2::PreProcess::SegmentCitations($rcite_text);

my @citations		= ();
my @valid_citations	= ();

sub trim($)
{
	my $string = shift;
	$string =~ s/^\s+//;
	$string =~ s/\s+$//;
	return $string;
}


# Process each citation
my $normalized_cite_text = "";
foreach my $citation (@{ $rraw_citations }) 
{

    my $cite_string = $citation->getString();  
 
    push @valid_citations, $cite_string;

    if (defined $cite_string && $cite_string !~ m/^\s*$/) 
    {
        $normalized_cite_text .= "<title> " . $citation->getString() . " </title>\n";
        push @citations, $citation;
    }
}


my $json = encode_json \@valid_citations;
# Terminal (e.g. putty) need to support UTF8 in order to view it at stdout
print $json . "\n";



