#!/bin/bash

################################################################################################################################################
# Script to generate user accounts in the VNF-WAC																							   #
################################################################################################################################################

# Define start and stop point for user generation
user_start = $1
user_end= $2

for (( user = ${user_start}; user <=${user_end}; user++ ))
do
#   ./bin/waccli user rm -u 5gtango${user}
echo 5gtango${user}
done
