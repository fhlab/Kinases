# Sequence-Function mapping of MKK1-ERK2 interactions reveals positive epistasis in the MKK1 D-domain
## Adaptation of InDelScanner scripts to highly combinatorial libraries

The scripts and JupyterLab notebooks in this repository can be used to reproduce the analysis in the title manuscripts. 

### Python and Conda dependencies
InDelScanner is a set of scripts that was developed and tested within the Anaconda tools. The environment is given in InDelScanner.yml. To install go to the InDelScanner directory and use:
```
conda env create -f InDelScanner.yml
```
Then activate the environment with `source activate InDelScanner` or `conda activate InDelScanner`. The latter is preferred for conda v.4.4 or higher, but can be finicky.

### Pre-processing
The folder `indels` contains the InDelScanner scripts. In this project, the sorted SpliMLib libraries were sequenced with Illumina paired-end sequenced. After read assembly, the merged reads are checked for correct library sequence and assembled by running `proteins.py`:
```
proteins.py -f FOLDER -r REFERENCE.FA
```
This command extracts the DNA sequence from FASTQ file that contains the randomised residues along with some flanking sequence, translated the DNA sequence into protein sequence, aligns it to the given protein sequence reference and writes the alignment files into the same folder. Next, the alignement files are parsed to generate a dictionary that lists all observed variants in this dataset.

### Statistics

The analysis is done in JupyterLab IPYNB notebooks, which are located in the folder `analysis`. In order, they are:
- Library_diversity: this notebook starts with preparation of the combined dictionary (integrating data from two sequencing runs) and reorganises the data into a Counter format for future convenience. The working directory and the location of the pickled dictionary need to be adapted in the notebook. A copy of the raw dictionary and the counter are provided in the `data` folder.

The analysis in this notebook is an exploration of sequence preferences in all three gates, before dataset curation (pie charts and variant counting for the Venn diagram). There is also a section on cross-position mututal information, which only gave a weak signal.

- Filtering_positives: this notebook explores how frequently the variants in the high gate appear in the other sequencing gates, and derives the curated dataset. It also generates plots for single site variants (relative to MKK1).

- Heatmaps: with the curated dataset in hand, this notebook generates all heatmap plots for single position preferences, joint enrichments and the testing for epistatic shifts in the fitness landscape.

- Generate_Hamming_Graph: This file generates the Hamming network for curated set of variants, as well as generating the node properties (various centrality statistics). Note that this takes a long time to run.

- Hamming_Graph_Partitioning: Starting with the `connected_annotated.graphml` graph that was generated in the previous file, this notebook performs the partitioning and analysis of the identified communities.
