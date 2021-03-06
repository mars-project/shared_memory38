#!/bin/bash

export UNAME="$(uname | awk '{print tolower($0)}')"
export PYTEST_CONFIG="--log-level=DEBUG --cov-report= --cov=mars --timeout=1500 -W ignore::PendingDeprecationWarning"

if [[ "$GITHUB_REF" =~ ^"refs/tags/" ]]; then
  export GITHUB_TAG_REF="$GITHUB_REF"
  unset CYTHON_TRACE
  export GIT_TAG=$(echo "$GITHUB_REF" | sed -e "s/refs\/tags\///g")
fi

if [[ $UNAME == "mingw"* ]] || [[ $UNAME == "msys"* ]]; then
  export UNAME="windows"
  CONDA=$(echo "/$CONDA" | sed -e 's/\\/\//g' -e 's/://')
  export PATH="$CONDA/Library:$CONDA/Library/bin:$CONDA/Scripts:$CONDA:$PATH"
  export PATH="$CONDA/envs/test/Library:$CONDA/envs/test/Library/bin:$CONDA/envs/test/Scripts:$CONDA/envs/test:$PATH"
else
  export CONDA="$HOME/miniconda"
  export PATH="$HOME/miniconda/envs/test/bin:$HOME/miniconda/bin:$PATH"
fi

export PYTHON=$(python -c "import sys; print('.'.join(str(v) for v in sys.version_info[:3]))")

if [ $UNAME == "darwin" ]; then
  export CC="gcc-10"
fi

function retry {
  retrial=5
  if [ $1 == "-n" ]; then
    retrial=$2
    shift; shift
  fi
  r=0
  while true; do
    r=$((r+1))
    if [ "$r" -ge $retrial ]; then
      $@
      return $?
    else
      $@ && break || true
      sleep 1
    fi
  done
}
alias pip="retry pip"
shopt -s expand_aliases
