#!/bin/bash

#Builds image 
# Doesn't work for common_grade_export

dir=${1}
docker build -t ${dir}_parser ${dir}/.
