#!/bin/bash

G_SYNOPSIS="

 NAME

	pypi.sh

 SYNOPSIS

	pypi.sh <name> <ver>

 ARGS
 	<name>
	The repo name.

	<ver>
	A version string to upload. Typically something like '0.20.22'.

 DESCRIPTION

	pypi.sh is a simple helper script to tag and upload a new version of pypi.sh 


"

if (( $# != 2 )) ; then
    echo "$G_SYNOPSIS"
    exit 1
fi

NAME=$1
VER=$2

git commit -am "v${VER}"
git push origin master
git tag $VER
git push origin --tags

rstcheck README.rst
python3 setup.py sdist
twine upload dist/${NAME}-${VER}.tar.gz

