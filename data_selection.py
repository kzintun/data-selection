#!/usr/local/bin/python
import sys, pdb, os, subprocess, gzip
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-m", "--mode", type=int, choices=[1,2], default=1, help="mode of operation, mode 1 - cross entropy, mode 2 - cross entropy difference")
parser.add_argument("-i", "--indomainLM", help="path to in-domain language model")
parser.add_argument("-o", "--outdomainLM", help="path to out-of-domain language model (should have same order as in-domain LM")
parser.add_argument("-d", "--datapool", help="path to data pool (1 sentence per line)")
parser.add_argument("-f", "--file", help="output file", default="output_sorted.txt")
parser.add_argument("-e", "--eval", help="evaluation file")
parser.add_argument("-r", "--order", help="lanuguage model order for evaluation", type=int, default=3, choices=[1,2,3,4,5,6,7,8,9,10])
parser.add_argument("-s", "--step", help="evaluation step size (in token percentage)", type=int, default=10) 
args = parser.parse_args()

def run_shell_cmd(command):
    output = subprocess.check_output(command, shell=True)
    return output

def check_LMorder(lm_file):
    order = -1
    with gzip.open(lm_file,'r') as f:
        f.readline()
        for line in f:
            if not line.strip():
                return order
            else:
                order+=1

def evaluate():
    #cut off first column which contains sentence score
    cmd = "cat mode"+str(args.mode)+args.file+" | cut -f2- > tmp_mode"+str(args.mode)+args.file
    run_shell_cmd(cmd)
    #count number of tokens
    token_size = run_shell_cmd("wc -w tmp_mode"+str(args.mode)+args.file).split()[0]

    for i in range(args.step,101,args.step):
        print("Calculating PPL for "+str(i)+"% (tokens) of "+args.file)
        cmd = "echo 'PPL for "+str(i)+"% (tokens) of "+args.file+":' >> mode"+str(args.mode)+\
                "evaluation.txt"
        run_shell_cmd(cmd)
        cmd = "awk '{ num_tokens += NF; if (num_tokens >= "+str(int(i*int(token_size)/100))+") {print NR; exit;} }' tmp_mode"+str(args.mode)+args.file
        line_size = run_shell_cmd(cmd)
        cmd = "head -n "+line_size.strip()+" tmp_mode"+str(args.mode)+args.file+" > tmp_mode"+ \
                str(args.mode)+str(i)+args.file
        run_shell_cmd(cmd)
        cmd = "ngram-count -text tmp_mode"+str(args.mode)+str(i)+args.file+ \
                " -kndiscount -interpolate -gt3min 0 -gt2min 0 -gt1min 0 -order "+ \
                str(args.order)+" -unk -lm tmp_lm_mode"+str(args.mode)+str(i)+args.file
        run_shell_cmd(cmd)
        cmd = "ngram -ppl "+args.eval+" -order "+str(args.order)+" -unk -lm tmp_lm_mode"+ \
            str(args.mode)+str(i)+args.file+" >> mode"+str(args.mode)+"evaluation.txt"
        run_shell_cmd(cmd)

if(args.mode == 1):
    print("***Opertaing in mode 1: cross entropy based data selection")
    if(not os.path.isfile(args.indomainLM)):
        print("***In domain language model is not found.")
        exit()
    elif(not os.path.isfile(args.datapool)):
        print("***Data pool is not found.")
        exit()
    elif(args.eval):
        if(not os.path.isfile(args.eval)):
            print("***Evaluation file is not found.")
            exit()
        if(args.step < 0 or args.step > 100):
            print("***Step size is not allowed, must be in range 1-100.")
            exit()

    #check order of input language model (must be in ARPA format)
    indomainLM_order = check_LMorder(args.indomainLM)
    #score sentences
    cmd = "ngram -ppl "+args.datapool+" -order "+str(indomainLM_order)+" -unk -lm "+ \
            args.indomainLM+" -debug 1 > tmp_mode"+str(args.mode)+args.file
    run_shell_cmd(cmd)
    #generate final output
    cmd = "head -n -1  tmp_mode"+str(args.mode)+args.file+" | grep 'logprob=.*ppl=.*ppl1=' |"+ \
            " cut -d' ' -f6 | paste - "+args.datapool+" | sort -g -k1,1 > mode"+str(args.mode)+ \
            args.file
    run_shell_cmd(cmd)
    #remove tmp files
    run_shell_cmd("rm -f tmp_mode1*")
    #Evaluate
    if(args.eval):
        run_shell_cmd("rm -f mode"+str(args.mode)+"evaluation.txt")
        evaluate()

    #remove tmp files
    run_shell_cmd("rm -f tmp_mode1*")
    run_shell_cmd("rm -f tmp_lm_mode1*")

elif(args.mode == 2):
    print("***Opertaing in mode 2: cross entropy difference based data selection")
    if(not os.path.isfile(args.indomainLM)):
        print("***In-domain language model is not found.")
        exit()
    elif(not os.path.isfile(args.outdomainLM)):
        print("***Out-of-domain language model is not found.")
        exit()
    elif(not os.path.isfile(args.datapool)):
        print("***Data pool is not found.")
        exit()
    elif(args.eval):
        if(not os.path.isfile(args.eval)):
            print("***Evaluation file is not found.")
            exit()
        if(args.step < 0 or args.step > 100):
            print("***Step size is not allowed, must be in range 1-100.")
            exit()

    #check order of input language model (must be in ARPA format)
    indomainLM_order = check_LMorder(args.indomainLM)
    outdomainLM_order = check_LMorder(args.outdomainLM)

    #score sentences with in-domain LM
    cmd = "ngram -ppl "+args.datapool+" -order "+str(indomainLM_order)+" -unk -lm "+ \
            args.indomainLM+" -debug 1 > tmp_mode"+str(args.mode)+args.file+"tmp1"
    run_shell_cmd(cmd)

    #generate output for in-domain LM
    cmd = "head -n -1  tmp_mode"+str(args.mode)+args.file+"tmp1 | "+\
            "grep 'logprob=.*ppl=.*ppl1=' | cut -d' ' -f6 | paste - "+args.datapool+\
            " > tmp_mode"+str(args.mode)+args.file+"tmp2"
    run_shell_cmd(cmd)

    #score sentences with out-of-domain LM
    cmd = "ngram -ppl "+args.datapool+" -order "+str(outdomainLM_order)+" -unk -lm "+ \
            args.outdomainLM+" -debug 1 > tmp_mode"+str(args.mode)+args.file+"tmp3"
    run_shell_cmd(cmd)

    #generate output for out-domain LM
    cmd = "head -n -1  tmp_mode"+str(args.mode)+args.file+"tmp3 | grep 'logprob=.*ppl=.*ppl1='|"+ \
            " cut -d' ' -f6 | paste - tmp_mode"+str(args.mode)+args.file+"tmp2 > tmp_mode"+ \
            str(args.mode)+args.file+"tmp4"
    run_shell_cmd(cmd)

    cmd = "cat tmp_mode"+str(args.mode)+args.file+ \
            '''tmp4 | awk '{a=$2/$1;$1=$2=""; print a,$0;}'|'''+ \
            "sed 's/ \+/ /g' | sort -g -k1,1 > mode"+str(args.mode)+args.file
    #cmd = "cat tmp4_"+args.file+''' | awk '{a=$2^1.2/$1; print a,$0;}' | '''+ \
    #        "sed 's/ \+/ /g' | sort -g -k1,1 > "+args.file
    run_shell_cmd(cmd)

    #remove tmp files
    run_shell_cmd("rm -f tmp_mode2*")
    #Evaluate
    if(args.eval):
        run_shell_cmd("rm -f evaluation.txt")
        evaluate()

    #remove tmp files
    run_shell_cmd("rm -f tmp_mode2*")
exit()
