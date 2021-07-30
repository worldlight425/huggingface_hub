import io
import json

import datasets
import tqdm
from huggingface_hub import HfApi


def iterate(pipe, dataset, f):
    for i, result in enumerate(tqdm.tqdm(pipe.iter(dataset))):
        write_result(result, f)


def iterate_slow(pipe, dataset, f):
    for i, item in enumerate(tqdm.tqdm(dataset)):
        try:
            result = pipe(item)
        except Exception as e:
            result = {"error": str(e)}

        write_result(result, f)


def write_result(result, f):
    f.write(json.dumps(result).encode("utf-8"))
    f.write(b"\n")


def batch(
    dataset_name: str,
    dataset_config: str,
    dataset_split: str,
    dataset_column: str,
    token: str,
    repo_id: str,
    use_gpu: bool,
    pipeline,
):
    dset = datasets.load_dataset(dataset_name, name=dataset_config, split=dataset_split)

    f = io.BytesIO()
    filename = f"data_{dataset_config}_{dataset_split}_{dataset_column}.txt"
    # TODO change to .iter(...) to get max performance on GPUs
    print("Start batch")

    if hasattr(pipeline, "iter"):
        iterate(pipeline, dset[dataset_column], f)
    else:
        iterate_slow(pipeline, dset[dataset_column], f)

    f.seek(0)

    api = HfApi()
    repo_id = repo_id
    try:
        api.upload_file(token, f, filename, repo_id, repo_type="dataset")
    except KeyError:
        print("Unchanged ? ")
