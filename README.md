# Data Selection
Data selection is one of the technique used to extract relevant data from the big text corpus for the given input text data. In our scenario, the input text data is the output/transcript of ASR, built from the LM that is not domain-specific enough. Hence, the data selection is applied to extract relevant domain-specific data to re-train LM and ultimately re-build ASR to produce a better transcript. 

# I. Requirements
TBA
# II. Inputs
* Data Corpus (e.g. Gigaword)
* Reference text 
* Vocab

#### Data Corpus
- A large text corpus with one sentence per line. **200 Million** sentenes.
- Used to extract relevant setences correponsding to ASR transcript.
- Placed inside "./input".
- Contact ztkyaw@ntu.edu.sg for download link.

#### Reference text
- A transcript(s) obtained from 1st pass decoding or manual transcript. 
- One sentence per line. Normalized w/ no punctuation and capitalization.
- Will be used as a reference of relevant data extraction.

#### Vocab
- An exisiting vocabulary of the LM. One word per line.

# III. Usage
Go to the project directory and run:

```sh
./run.sh --steps 1-4 <path to data corpus> <path to ref transcript> <path to vocab> <output-dir>

#step 1 - produce in-domain LM from given input text file (ref transcript)
#step 2 - produce out-domain LM from the 1% of data corpus (randomly selected)
#step 3 - perform data-selection technique and produced the output data corpus with sentences ranked by perplexity scores ( lower = more relevant )
#step 4 - prepare the output for re-training LM ( final output = ./output/$output-dir/selected_data
```
Example with sbatch
```sh
sbatch --nodelist=node04 -o ./log/data_select.log  run.sh --steps 1  ./input/data_pool_RR_1  ./input/judge-sg.txt  ./input/vocabs.txt ./output/judge-data-110819
```

# IV. Author
* Khassanov Yerbolat - yerbolat002@e.ntu.edu.sg
* Kyaw Zin Tun - ztkyaw@ntu.edu.sg
