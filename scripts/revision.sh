#!/bin/bash
NEXT_ID=`ls changeme/db/migrations/versions/* | grep -P '/\d{4}_.*\.py$' | wc -l`
	sbuilder manager db revision -m $@ --rev-id=`printf "%04d" ${NEXT_ID}`


