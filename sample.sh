#!/bin/bash

python3 filter_corp.py --input EMEA.de-en.de EMEA.de-en.en \
                       --output filtered.de  filtered.en   \
                       --max-digits 5                      \
                       --unique                            \
                       --min-tokens 5                      \
#--limit 50
#--sort-keys length-descending \
