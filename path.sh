export KALDI_ROOT=/local/tools/kaldi-2019
# export KALDI_BIN=$KALDI_ROOT/bin-feb-06-2017
# export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:

export PATH=$PWD/utils/:$KALDI_ROOT/tools/openfst/bin:$KALDI_ROOT/tools/kaldi_lm:/home/zin/Downloads/srilm_source/bin/i686-m64:$PWD:$PATH
export PATH=$KALDI_ROOT/tools/sph2pipe_v2.5:$PATH
#export PATH=$KALDI_ROOT/tools/sph2pipe_v2.5:/home/opt/tools/NIST/sctk-2.4.8/bin:/home2/hhx502/cntk-oct-04-2016/build/release/bin:$PATH
[ ! -f $KALDI_ROOT/tools/config/common_path.sh ] && echo >&2 "The standard file common_path.sh is not present -> Exit!" && exit 1
. $KALDI_ROOT/tools/config/common_path.sh
export LC_ALL=C
