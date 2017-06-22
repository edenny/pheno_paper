#!/bin/bash
# quick and dirty script to search to load data by genus for each project

PROJECTS=(pep725 npn)
#GENERA=(Acer Aesculus Alnus Artemisia Betula Cornus Corylus Fagus Forsythia Fragaria Fraxinus Larix Malus Picea Pinus Prunus Quercus Rubus Salix Sambucus Sorbus Symphoricarpos Syringa Taraxacum Tilia)
#GENERA=(Acer)
GENERA=(Aesculus Alnus Artemisia Betula Cornus Corylus Fagus Forsythia Fragaria Fraxinus Larix Malus Picea Pinus Prunus Quercus Rubus Salix Sambucus Sorbus Symphoricarpos Syringa Taraxacum Tilia)
#GENERA=(Acer Aesculus Alnus Betula Fagus Forsythia Fraxinus Pinus Prunus Quercus Salix Syringa)

for genus in ${GENERA[@]}; do
  echo "-----------------------------------------"
  echo "Processing $genus"
  echo "-----------------------------------------"

  echo "Creating namespace = " $genus
  ./createNamespace.sh $genus
  echo ""

  for project in ${PROJECTS[@]}; do
    FILES=(/home/jdeck88/code/pheno_paper/data/$project/output_reasoned/$genus*.ttl)
    echo ""
    echo "Processing project = " $project
    for file in ${FILES[@]}; do
      echo ""
      echo "    " curl \
        -sS -X POST -H 'Content-Type:text/turtle' \
        --data-binary '@'$file \
        http://localhost:9999/blazegraph/namespace/$genus/sparql   
      curl \
        -sS -X POST -H 'Content-Type:text/turtle' \
        --data-binary '@'$file \
        http://localhost:9999/blazegraph/namespace/$genus/sparql   
      done
  done
done
