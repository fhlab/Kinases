#!/usr/bin/env python3

import sys
import pickle
import re
import os
import csv
import argparse
import math
import pprint

from string import ascii_lowercase
from collections import Counter

from Bio import SeqIO, AlignIO
from Bio.SeqRecord import SeqRecord
from Bio.Alphabet import IUPAC
from Bio.Seq import Seq
from Bio.Emboss.Applications import NeedleallCommandline

from indels.ind import trim_read, findEnds, endMatch, findGap, gapAlign

# Demand Python 3.
if sys.version_info[0] < 3:
    print("Python 3 is required, but you are using Python %i.%i.%i") % (
        sys.version_info[0], sys.version_info[1], sys.version_info[2])
    sys.exit(1)


def fastq_to_prot_gen(fastq):
    """
    Read in a fastq file. Start with constant sequence and capture the following 45
    :param fastq:
    :param constant_seq:
    :return:
    """
    for dna_record in SeqIO.parse(fastq, 'fastq'):
        dna = str(dna_record.seq)
        # first check whether it fits Remkes' library design
        gen = 'ATGCCCAAGAAGAAG[ACTG]{3}ACG([ACTG]{3})?CCG(GCG)?[ACTG]{3}CAG[ACTG]{3}AAC[ACTG]{3}GCCCCCGACGGC'
        good_seq = re.search(gen, dna)
        if not good_seq:
            continue
        # then extract the orf and translate it
        gene = re.search('ATGCCCAAGAAGAAG[ACTG]{36}', dna)
        orf = Seq(gene.group(0), IUPAC.unambiguous_dna)
        protein = orf.translate()

        yield SeqRecord(protein, id=dna_record.id)


def process_all_fastq(folder):
    """
    Scan all fastq files in input folder and convert them to protein sequence.
    :param folder:
    :return:
    """
    prot_files = []
    print(os.listdir(folder))
    for fqfile in os.listdir(folder):
        if fqfile.endswith('.fastq'):
            fq_path = os.path.join(folder, fqfile)
            prefix, ending = fqfile.rsplit('.', 1)
            print('Converting fastq file {0}'.format(fqfile))
            generator = fastq_to_prot_gen(fq_path)
            SeqIO.write(generator, prefix + '.filt.prot.fa', 'fasta')
            prot_files.append(prefix + '.filt.prot.fa')

    return prot_files


def protein_needle(prot_files, reffile):
    """
    Use the Emboss Needle package to align fastq read to reference, return trimmed reads from the alignment
    :param prot_files: list of fastq file
    :param reffile: name of reference file
    :return:
    """
    aln_files = []

    for fqname in prot_files:
        prefix, suffix = os.path.splitext(fqname)
        alnname = prefix + '.aln'
        needle_cline = NeedleallCommandline(r'needleall', asequence=reffile, bsequence=fqname,
<<<<<<< HEAD
                                            gapopen=3, gapextend=5, datafile='PNULL',
                                            verbose=False, outfile=alnname, aformat='fasta') # alternative: (r'/opt/emboss/bin/needleall'
=======
                                            gapopen=3, gapextend=5, datafile='PNULL',auto=True, options=False,
                                            verbose=False, outfile=alnname, aformat='fasta')
>>>>>>> master
        needle_cline()

    return aln_files


def indel_len(sequence, start):
    l = 0
    while sequence[start + l] == '-':
        l += 1
    return l


def format_prot_insertion(ref_index, aa):
    inslist = []
    stop = False
    for i in range(len(aa)):
        inslist.append(str(ref_index) + ascii_lowercase[i] + aa[i])
        if str(aa[i]) == '*':
            stop = True
            break

    return stop, inslist


def find_protein_short(read, ref, ends):

    prot_short = []

    i = ends.get('start')
    ref_index = ends.get('start') + 1  # reference amino acid index

    while i < ends.get('end'):
        if read[i] != ref[i]:  # found a mutation
            if read[i] == '-':  # found a deletions
                prot_short.append(str(ref_index) + 'Δ')
                i += 1
                ref_index += 1
            elif ref[i] == '-':  # found an insertion
                # check the length: to handle insertions of multiple AAs correctly
                l = indel_len(ref, i)
                stop, inslist = format_prot_insertion(ref_index - 1, read[i:i+l])
                prot_short += inslist  # adding two lists together
                if stop:
                    break
                i += l
            else:  # substitutions
                prot_short.append(str(ref_index) + read[i])
                i += 1
                ref_index += 1
        else:
            i += 1
            ref_index += 1

    if prot_short == []:
        short = 'wt'
    else:
        short = '/'.join(prot_short)

    return short


def one_gate(alignment):

    counts = {}

    for pair in AlignIO.parse(alignment, "fasta", seq_count=2):
        # both read and ref are MutableSeq
        ref = str(pair[0].seq)
        read = str(pair[1].seq)
        readname = pair[1].id

        ref, read = trim_read(ref, read)

        # check that there is no frame shift or gross mistranslation
        ends = findEnds(read, ref, 0)
        if not endMatch(read, ref, ends, 2):
            continue

        protein = find_protein_short(read, ref, ends)

        try:
            counts[protein] += 1
        except KeyError:
            counts[protein] = 1

    # count the mutations
    n = 0
    threshold = 10
    for error in counts.keys():
        if counts[error] > threshold:
            n += 1

    print('Fount {0} total protein mutations, of which {1} have more than {2} counts'
          .format(len(counts), n, threshold))

    return counts


def count_all_gates(folder):

    all_references = {}

    print(os.listdir(folder))
    for alnfile in os.listdir(folder):
        if alnfile.endswith('.aln'):
            aln_path = os.path.join(folder, alnfile)
            refname, fraction, suffix = alnfile.split(".", 2)
            print('Counting alignment {0} in background {1} and activity fraction {2}'
                  .format(alnfile, refname, fraction))

            if refname not in all_references.keys():
                all_references[refname] = {}

            all_references[refname][fraction] = one_gate(aln_path)

    return all_references


def count_all_observed(all_ref):
    for background in all_ref.keys():
        for fraction in all_ref[background].keys():
            prot = 0
            cnt = 0
            for protein, count in all_ref[background][fraction].items():
                cnt += count
                prot += 1
            print('In background {0} fraction {1} found {2} total mutations with {3} total reads'.format(
                background, fraction, prot, cnt))






if __name__ == "__main__":
    """
    Arguments:
    1.   Alignment of sequencing reads to a reference sequence in FASTA format. The
         reference comes before read sequence. (>Ref, seq, >Read, seq).
    (2.) Optional: DEBUG print a coloured representation of mismatches
    """
    parser = argparse.ArgumentParser(description='Finds all in-frame mutations in a gene')
    parser.add_argument('-f', '--folder', help='Folder containing multiple sequence alignments', required=True)
    parser.add_argument('-r', '--reference', required=False)
    parser.add_argument('-o', '--output', required=False)
    args = parser.parse_args()

    # Convert fq files to protein fasta
    prot_files = process_all_fastq(args.folder)
    # Then make the alignment
    # prot_files = ['mek.high.filt.prot.fa', 'mek.low.filt.prot.fa', 'mek.med.filt.prot.fa']
    aln_files = protein_needle(prot_files, args.reference)
    
    # On the first run, analyse all *.aln files in the target folder and create a dictionary of errors
    # Structure: all_ref[background][fraction][protein mutation] = all data about the mutations
    all_ref = count_all_gates(args.folder)
    
    with open('Remkes_protein_low.p', 'wb') as f:
        pickle.dump(all_ref, f)
