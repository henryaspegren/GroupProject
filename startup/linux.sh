#!/bin/bash

echo -n "Enter your SRCF user name (=crsid): "
read crsid
ssh -L 3307:localhost:3306 $crsid@shell.srcf.net