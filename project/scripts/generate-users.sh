#!/bin/bash

################################################################################################################################################
# Script to generate user accounts in the VNF-WAC																							   #
################################################################################################################################################

# Define start and stop point for user generation
user_start = $1
user_end = $2

for (( user = ${user_start}; user <=${user_end}; user++ ))
do
  ./bin/waccli user add -u 5gtango${user} -d quobis -r user 
  ./bin/waccli credentials add -t basic -d quobis -u 5gtango${user} --basic-password 5gtango${user}
done

#inlude start and stop in variables 