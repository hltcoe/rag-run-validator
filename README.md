# RAG Run Validator

A simple Python package for validating a RAG run for TREC RAG-related tracks, including 
[RAGTIME](https://trec-ragtime.github.io/), [RAG](https://trec-rag.github.io/), 
[DRAGUN](https://trec-dragun.github.io/), [BioGen](https://dmice.ohsu.edu/trec-biogen/),
and [iKAT](https://www.trecikat.com/). 

The default schema can be found in `./rag_run_validator/defaut.json`, which allows the citation for each response
sentence to be either a list of document IDs or a dictionary of document ID to score. 

## Get Started
```bash
pip install git+https://github.com/hltcoe/rag-run-validator.git
```

## Usage

You can validate the run at command line through our cli interace. 
```bash
rag_run_validator your_run.jsonl
```

For validating against a specific set of topics to ensure all required topics are included 
in the run, you can provide the topic .jsonl file to the validator.
If the `limit` field is included in the topic object, the validator will also check for the length
limit (default to character count). 
```bash
rag_run_validator your_run.jsonl --topics topic_file.jsonl
```

You can also manually specify the length and specify the length limit mode for other tasks.
```bash
rag_run_validator your_run.jsonl --limit 1000 --length_limit_mode words
```

Please refer to `rag_run_validator --help` for more detail.
```
usage: TREC RAG-related tracks output format validator [-h] [--schema SCHEMA]
                                                       [--topics TOPICS]
                                                       [--limit LIMIT]
                                                       [--length_limit_mode {characters,words}]
                                                       [--strict_on_length]
                                                       [--verbose] [--stop_at_error]
                                                       run

positional arguments:
  run                   input .jsonl run file for validation.

options:
  -h, --help            show this help message and exit
  --schema SCHEMA       schema .json file for validation
  --topics TOPICS       topic .jsonl file for validating the length and topic set;
                        will override `--limit` if topics file is provided.
  --limit LIMIT         length limit
  --length_limit_mode {characters,words}
                        definition of length limit
  --strict_on_length    whether treat exceeding the length limit as an error
  --verbose             verbose output for the validation errors.
  --stop_at_error       stop at the first error encountered.
```

Or through Python interface
```python
from rag_run_validator import validate

your_run = [
    {"metadata": {...}, "responses": [{"text": ...}]}
]

# a full run
validate(your_run)
# a single topic
validate(your_run[0])
# or a path to the file
validate("path_to_your_run.jsonl")
# a custom schema
validate("path_to_your_run.jsonl", {"$schema": ...})
```
The `validate` function would throw an `ValidationError` execption if the input run does not comply to the schema. 

## Example Run

The default schema allows a run of the following format. 
```json
{
    "metadata": {
        "team_id": "my_fantastic_team",
        "run_id": "my_best_run_02", 
        "topic_id": "101",
    },
    "responses": [
        {
            "text": "Sky is blue.",
            "citations": {
                "docid001": 0.3,
                "docid003": 0.1,
            }
        },
        {
            "text": "The moon is made out of blue cheese.",
            "citations": {
                "docid002": 0.7,
            }
        },
        {
            "text": "This is all.",
            "citations": {}
        },
    ],
    "references": [
        "docid0001",
        "docid0002",
        "docid0003",
    ]
}
```

Or with simply a list of citations.
```json
{
    "metadata": {
        "team_id": "my_fantastic_team",
        "run_id": "my_best_run_02", 
        "topic_id": "101",
    },
    "responses": [
        {
            "text": "Sky is blue.",
            "citations": [
                "docid001",
                "docid003",
            ]
        },
        {
            "text": "The moon is made out of blue cheese.",
            "citations": [
                "docid002"
            ]
        },
        {
            "text": "This is all.",
            "citations": []
        }
    ],
    "references": [
        "docid0001",
        "docid0002",
        "docid0003",
    ]
}
```

## Credit

Thanks to all RAG-related coordinators at TREC and others for the discussion. 
Please consider participate in the tracks mentioned at the top of this README. 
All coordinators would appreciate your participation and effort in improving 
RAG systems and evaluation. 

## Contact

If you have any question, feel free to email [Eugene Yang](mailto:eugene.yang@jhu.edu) 
or raise an issue in this repository. 
