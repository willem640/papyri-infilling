import re

# this is a WIP (TODO here), this solves ~5 papyri, out of ~10,000
exceptions = {
        "zpe.152.181_2": "zpe.152.181/"
        }

regex_exceptions = {
    r"(.*?) *" : r"\1" # remove trailing spaces
        }

def get_exception(ddbdb_id):
    literal_exception = exceptions.get(ddbdb_id)
    if literal_exception is not None:
        return literal_exception
    for regex, sub in regex_exceptions.items():
        ddbdb_id = re.sub(regex, sub, ddbdb_id)
    return ddbdb_id 

