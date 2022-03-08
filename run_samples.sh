#!/bin/bash

PREFIX=$(dirname $(readlink -f "$0"))
WORKDIR="./tmp"

mkdir -p $WORKDIR


function sample_demosaic {
	dataset=$1
	workdir=$2
	for l in $(seq 1 5)
	do
		for h in L R
		do
			src="${dataset}/img_L${l}_${h}.png"
			dst="$WORKDIR/preview_$(basename $dataset)_img_L${l}_${h}.jpg"
			echo "$src -> $dst"
			python3 "$PREFIX/sample_demosaic.py" "$src" "$dst"
		done
	done
}

function sample_triangulate {
	dataset=$1
	workdir=$2
	dst="$workdir/$(basename $dataset).ply"
	echo "$dst"
	python3 "$PREFIX/sample_triangulate.py" "$dataset" "$dst"
}

for dataset in pig stone book lemon dinosaur
do
	if [ ! -d $dataset ]; then
		echo "[ERROR] cannot find ./$dataset"
		continue
	fi

	sample_demosaic ./$dataset $WORKDIR
	sample_triangulate ./$dataset $WORKDIR
done

