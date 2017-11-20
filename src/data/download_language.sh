# Created by David Goldstein on 11/19/2017
# downloads html pages using curl and parses with w3m

# currently supported :
#     - english

# USAGE : ./download...ge ${language}

language=$1
if [ ! -d "${language}" ]; then
  echo "No such language supported ${language}"
  exit 1
fi

# run python script to write words to large json
time python "${language}/writeSynonymJson.py"

