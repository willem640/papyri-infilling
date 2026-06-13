# Scripts to add metadata from the HGV and DdbDP to MAAT in a mongodb database

To run these scripts, you have to run a mongodb instance. I recommend using the docker image:

```bash
$ docker pull mongodb/mongodb-community-server:latest
$ docker run --name mongodb -p 27017:27017 -d mongodb/mongodb-community-server:latest

```
I recommend MongoDB compass for inspecting and/or downloading the data.
You should clone papyri/IDP.data in this folder and put maat.json here as well. If you wish to name things differently, see the scripts for some env variables.

Then, run the scripts in order to insert the various metadata into the database. It will only put DdbDP papyri in there. It is reasonably complete but may miss some records if the EpiDoc is irregular.

The database should have the following format for each record:
```
{
    // the following fields are from MAAT:
    corpus_id: string, // always DDbDP
    file_id: string, // for example: cde.85.245
    block_index: uint, // blocks for the same filename
    id: string, // "{corpus_id}/{file_id}/{block_index}"
    title: string, // often the same as filename
    material: string, // "papyrus"
    language: string, // "grc"
    training_text: string, // text with infillings
    test_cases: Array<{
        case_index: uint, // increasing
        id: string, // "{corpus_id}/{file_id}/{block_index}/{case_index}"
        test_case: string // all infillings are substituted, except one which will be like [..].
    }>,
    // these are added by my scripts:
    hgv_id: string, // often the same as Trismegistos ID, but may be "{tm_id}a"
    tm_id: string, // Trismegistos ID
    hgv_title: string, // title as given by the HGV
    orig_place: {
        text: string, // nearly always given
        TM: string, // Trismegistos place ID. Often given
        PL: string // Pleiades place ID. Rarely given
    },
    date_range: {
        min: {
            y: int, // may be negative for BCE
            m: uint,
            d: uint
        },
        max: {
            y: int, // may be negative for BCE
            m: uint,
            d: uint
        }
    }


}


```

