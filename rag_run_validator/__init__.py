import argparse
from pathlib import Path

import json
import jsonschema
from jsonschema.exceptions import ValidationError

default_schema = json.loads((Path(__file__).absolute().parent / "data" / "default.json").read_text())

def read_jsonl(fn):
    with open(fn) as f:
        yield from map(json.loads, f)

def validate(run, schema=None):
    if isinstance(run, str):
        if Path(run).exists():
            run = list(read_jsonl(run))
        else:
            run = json.loads(run)
    if isinstance(run, dict):
        run = [run]

    for r in run:
        jsonschema.validate(r, schema if schema is not None else default_schema)

def cli():
    parser = argparse.ArgumentParser("TREC RAG-related tracks output format validator")
    parser.add_argument("run", help="input .jsonl run file for validation. ")
    parser.add_argument("--schema", default=None, help="schema .json file for validation")

    parser.add_argument(
        "--verbose", action="store_true", default=False,
        help="verbose output for the validation errors."
    )
    parser.add_argument(
        "--stop_at_error", action="store_true", default=False,
        help="stop at the first error encountered."
    )

    args = parser.parse_args()

    schema = json.loads(Path(args.schema).read_text()) if args.schema is not None else default_schema
    
    all_passed = True
    for i, topic_run in enumerate(read_jsonl(args.run)):
        try:
            validate(topic_run, schema)
        except ValidationError as e: 
            all_passed = False
            print(f"Validation error on line {i+1}")
            if args.verbose:
                print(e)
            if args.stop_at_error:
                break

    if not all_passed:
        exit(1)
    exit(0)

if __name__ == '__main__':
    cli()