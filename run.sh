#!/bin/bash

# This script selects training data for building task specific language models.
# The selection procedure is performed by employing available in-domain data
# (e.g. ASR output) to select relevant data from the large corpus.

################## DATA ##############################################################
# You need following data:
#   1) Large corpus - 1 sentence per line, preprocessed (e.g. lower case).
#   2) In-domain data - 1 sentence per line, preprocessed.

################## TOOLS #############################################################
# First install following tools:
#   1) XenC     https://github.com/antho-rousseau/XenC
#   2) SRILM    http://www.speech.sri.com/projects/srilm/

######################################################################################

. path.sh

echo 
echo "## LOG: $0 $@"
echo

# begin options
steps=

# end options

. parse_options.sh || exit 1

function Usage {
 cat<<EOF
 
 [Example]: $0 --steps N /local/Data_sel/input/datapool.txt \
 /local/Data_sel/input/judge.txt \
 /local/Data_sel/input/vocab.txt \
 /local/Data_sel/output/exp-new-1 

EOF
}

if [ $# -ne 4 ]; then
	Usage && exit 1
fi

steps=$(echo $steps | perl -e '$steps=<STDIN>;  $has_format = 0;
  if($steps =~ m:(\d+)\-$:g){$start = $1; $end = $start + 10; $has_format ++;}
        elsif($steps =~ m:(\d+)\-(\d+):g) { $start = $1; $end = $2; if($start == $end){}elsif($start < $end){ $end = $2 +1;}else{die;} $has_format ++; }  
      if($has_format > 0){$steps=$start;  for($i=$start+1; $i < $end; $i++){$steps .=":$i"; }} print $steps;' 2>/dev/null)  || exit 1

if [ ! -z "$steps" ]; then
  for x in $(echo $steps|sed 's/[,:]/ /g'); do
    index=$(printf "%02d" $x);
    declare step$index=1
  done
fi



corpus=$1 # Path to the large corpus (comment: change it to input arguments if required)
indomain=$2 # Path to the in-domain data (comment: change it to input arguments if required)
vocab=$3 # Path to the vobulary used in your NLP application (e.g. ASR), 1 word per line
outDir=$4 

# Order of the LM for data selection (default is 2)
order=3
curDir=$(dirname "$(realpath $0)")
DATE=`date +%Y-%m-%d-%H:%M`
#outDir=$curDir/output/exp$DATE
log_file=$outDir/dataSel.log

[ -d $outDir ] || mkdir -p $outDir
if [ ! -z $step01 ]; then
	echo "## LOG (step01, $0): Build in-domain LM" >> $log_file
	# Build in-domain LM, using witten-bell smoothing which is insensitive to data size
	
	ngram-count -text $indomain -order $order -wbdiscount -unk -vocab $vocab -lm $outDir/in_domain_lm.wb$order.gz >> $log_file 2>&1
	
	echo "## LOG (step01, $0): Build in-domain LM done" >> $log_file

fi

if [ ! -z $step02 ]; then
	echo "## LOG (step02, $0): Randomly select sentences from corpus to build out-domain LM" >> $log_file
	# Build out-of-domain LM
	# 1) Randomly select a portion of the corpus, in this case we are selecting 1% (1992192) of the large corpus
	total_lines=($(wc -l $corpus))
	rand_lines=$(bc <<< "scale=1; 0.01*${total_lines[0]}")
	int_rand_lines=${rand_lines%.*}

	shuf -n $int_rand_lines $corpus > $outDir/rand_portion.txt
	echo "## LOG (step02, $0): Random sentence selection done" >> $log_file

	echo "## LOG (step02, $0): Build out-domain LM" >> $log_file
	# 2) Build out-of-domain LM
	ngram-count -text $outDir/rand_portion.txt -order $order -wbdiscount -lm $outDir/out_domain_lm.wb$order.gz -unk -vocab $vocab >> $log_file 2>&1
	echo "## LOG (step02, $0): Build out-domain LM done" >> $log_file
fi

if [ ! -z $step03 ]; then
	echo "## LOG (step03, $0): Data selection" >> $log_file
	#Data selection script, tested on Python 2.7.12
	python data_selection.py -m 2 -i $outDir/in_domain_lm.wb$order.gz -o $outDir/out_domain_lm.wb$order.gz -d $corpus -f expOutput.txt
	mv mode2expOutput.txt $outDir/mode2expOutput.txt
	echo "## LOG (step03, $0): Data selection done" >> $log_file
fi

if [ ! -z $step04 ]; then
	echo "## LOG (step04, $0): Select top 10%, Extract text portion, remove single utterance word" >> $log_file
	tenPct=19921910
	head -n $tenPct $outDir/mode2expOutput.txt | cut -d " " -f2- | awk 'NF>1' > $outDir/selected_data
	echo "## LOG (step04, $0): Select top 10%, Extract text portion, remove single utterance word done" >> $log_file
fi

#if [ ! -z $step05 ]; then
#        echo "## LOG (step05, $0): Select top 10 % of lowest perplexity sentences" >> $log_file
        # Take for example top %10 
#        head -n 19921910 $outDir/mode2expOutput.txt > $outDir/selected_data.txt
#        echo "## LOG (step05, $0): selection done" >> $log_file
#fi


#if [ ! -z $step06 ]; then

#	echo "## LOG (step06, $0): Crop text from final output" >> $log_file
	# Lastly remove the scores from the selected data as follows:
#	cat $outDir/selected_data.txt | cut -d " " -f2- > $outDir/selected_data_text.txt
#	echo "## LOG (step06, $0): Cropping done" >> $log_file

#fi


#if [ ! -z $step07 ]; then
#	echo "## LOG (step07, $0): Remove single utterance words from selected data" >> $log_file
#	awk  'NF>1' $outDir/selected_data_text >> $outDir/selected_data_test_noSgUtt.txt
#	echo "## LOG (step07, $0): Remove single utterance words done" >> $log_file
#fi
