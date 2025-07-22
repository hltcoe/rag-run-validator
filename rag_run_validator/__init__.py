from typing import Dict, List
import argparse
from pathlib import Path
import io

import unicodedata
import json
import jsonschema
from jsonschema.exceptions import ValidationError

default_schema = json.loads((Path(__file__).absolute().parent / "data" / "default.json").read_text())

def read_jsonl(fn):
    if isinstance(fn, io.IOBase):
        yield from map(json.loads, fn)
    else:
        with open(fn) as f:
            yield from map(json.loads, f)

def _as_list_of_runs(run) -> List[Dict[str, Dict]]:
    if isinstance(run, str):
        if run.startswith("[") or run.startswith("{"):
            return list(read_jsonl(io.StringIO(run)))
        else:
            return list(read_jsonl(run))
            
    if isinstance(run, dict):
        return [run]
    
    return run

def validate(run, schema=None):
    run = _as_list_of_runs(run)
    for r in run:
        jsonschema.validate(r, schema if schema is not None else default_schema)

def validate_length(run, length_limit=None, length_limit_mode='characters'):
    run = _as_list_of_runs(run)
    for r in run: 
        text = " ".join(s['text'] for s in r['responses'])
        if length_limit_mode == 'characters':
            length = len(unicodedata.normalize('NFKC', text))            
        elif length_limit_mode == 'words':
            length = len(text.split())
        else:
            raise RuntimeError(f"Unsupported length limit mode `{length_limit_mode}`")
            
        assert length <= length_limit, \
            f"Response in topic {r['metadata']['topic_id']} is too long ({length_limit_mode}) "\
            f"-- {length} > {length_limit}"

def cli():
    parser = argparse.ArgumentParser("TREC RAG-related tracks output format validator")
    parser.add_argument("run", help="input .jsonl run file for validation. ")
    parser.add_argument("--schema", default=None, help="schema .json file for validation")
    parser.add_argument(
        "--topics", default=None,
        help="topic .jsonl file for validating the length and topic set; "
             "will override `--limit` if topics file is provided."
    )
    parser.add_argument("--limit", type=int, default=None, help="length limit")
    parser.add_argument(
        "--length_limit_mode", choices=['characters', 'words'], default="characters",
        help="definition of length limit"
    )
    parser.add_argument(
        "--strict_on_length", action="store_true",
        help="whether treat exceeding the length limit as an error"
    )

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
    topics, found_topics = {}, []
    if args.topics is not None:
        topics = {
            topic['topic_id']: topic for topic in read_jsonl(args.topics)
        }
    
    all_passed = True
    containing_topics = []
    for i, topic_run in enumerate(read_jsonl(args.run)):
        try:
            validate(topic_run, schema)

            topic_id = topic_run['metadata']['topic_id']
            containing_topics.append(topic_id)

            length_limit = None
            if topic_id in topics \
                and 'limit' in topics[topic_id]:
                length_limit = topics[topic_id]['limit']
            elif args.limit is not None:
                length_limit = args.limit
            
            if length_limit is not None:
                validate_length(topic_run, length_limit, args.length_limit_mode)

        except ValidationError as e: 
            all_passed = False
            print(f"[Error:{i+1}] Format -- " + str(e))
            
        except AssertionError as e:
            if args.strict_on_length:
                all_passed = False
            print(f"[{'Error' if args.strict_on_length else 'Warning'}:{i+1}] " + str(e))
        
        if not all_passed and args.stop_at_error:
            break

    else:
        # check for topic set if all formatting check pass
        if len(topics) > 0:
            missing_topics = set(topics.keys()) - set(containing_topics)
            if len(missing_topics) > 0:
                all_passed = False
                print(f"[Error] Missing topics: {missing_topics}")

    if not all_passed:
        exit(1)
    exit(0)

if __name__ == '__main__':
    cli()