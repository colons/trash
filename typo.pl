use Text::Typoifier;
 
$t = new Text::Typoifier;
$t->errorRate(7);

print $t->transform($ARGV[0]);
