python -m spacy train config_spacy_train.cfg --output model --verbose -g 0

echo "Eval best:"
spacy evaluate model/model-best/ test.spacy -g 0 -o model/eval-best.json | sed -e 's/\x1b\[[0-9;]*m//g' | tee model/eval-best.txt
echo "Eval last:"
spacy evaluate model/model-last/ test.spacy -g 0 -o model/eval-last.json | sed -e 's/\x1b\[[0-9;]*m//g' | tee model/eval-last.txt
cp test.spacy model/
