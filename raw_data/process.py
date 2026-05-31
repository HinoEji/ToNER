from datasets import Dataset, DatasetDict
import json


def read_conll(path):
    with open("raw_data/tag_map.json", encoding="utf8") as f:
        tag_map = json.load(f)
    samples = []

    tokens = []
    tags = []

    with open(path, encoding="utf8") as f:
        for line in f:
            line = line.strip()

            if not line:
                if tokens:
                    samples.append({
                        "tokens": tokens,
                        "tags": tags
                    })

                tokens = []
                tags = []
                continue

            token, tag = line.split("\t")

            tokens.append(token)
            tags.append(tag_map[tag])

    if tokens:
        samples.append({
            "tokens": tokens,
            "tags": tags
        })

    return samples


if __name__ == "__main__":
   dataset = DatasetDict({
    "train": Dataset.from_list(read_conll("raw_data/train.txt")),
    "validation": Dataset.from_list(read_conll("raw_data/dev.txt")),
    "test": Dataset.from_list(read_conll("raw_data/test.txt")),
})

dataset.save_to_disk("./data/my_data")