import random
from argparse import ArgumentParser

from datasets import Dataset, DatasetDict, load_from_disk
from sentence_transformers import (
    SentenceTransformer,
    SentenceTransformerTrainer,
    SentenceTransformerTrainingArguments
)
from sentence_transformers.losses import TripletLoss

from utils.flat import (
    get_tag_map,
    get_keys,
    get_entity_type_desc
)

MODEL_PATH = "BAAI/bge-m3"
DATA_PATH = "./data/my_data"

random.seed(7777)


def process(raw_data, mode="train", data_type="WNUT2017"):
    tag_map = get_tag_map(data_type)
    schemas = get_keys(data_type)
    entity_type_desc = get_entity_type_desc(data_type)

    data = []

    for line in raw_data:
        sentence = " ".join(line["tokens"])

        pos_name = []
        neg_name = []

        random.shuffle(schemas)

        tags = line.get("ner_tags", line.get("tags"))

        try:
            labels = set(
                tag_map[x][tag_map[x].index("-") + 1:].lower()
                for x in tags
                if x != 0
            )
        except:
            labels = set(
                tag_map[x].lower()
                for x in tags
                if x != 0
            )

        for name in labels:
            if name not in pos_name:
                pos_name.append(name)

        for name in schemas:
            if name not in pos_name:
                neg_name.append(name)

        if mode == "train":
            for pos in pos_name:
                for neg in neg_name:
                    data.append(
                        {
                            "anchor": sentence,
                            "positive": f"{pos}: {entity_type_desc[pos]}",
                            "negative": f"{neg}: {entity_type_desc[neg]}"
                        }
                    )
        else:
            data.append(
                {
                    "input": sentence,
                    "label": list(labels)
                }
            )

    return data


def load_train_data(data_path):
    dataset = {}
    data_type = data_path.split("/")[-1]

    raw_dataset = load_from_disk(data_path)

    for split in ["train", "validation"]:
        raw_data = [x for x in raw_dataset[split]]

        dataset[split] = Dataset.from_list(
            process(
                raw_data,
                mode="train",
                data_type=data_type
            )
        )

    return DatasetDict(dataset)


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument(
        "--data_path",
        type=str,
        default=DATA_PATH
    )

    parser.add_argument(
        "--model_path",
        type=str,
        default=MODEL_PATH
    )

    parser.add_argument(
        "--batch_size",
        type=int,
        default=2
    )

    parser.add_argument(
        "--epochs",
        type=int,
        default=1
    )

    parser.add_argument(
        "--learning_rate",
        type=float,
        default=2e-5
    )

    parser.add_argument(
        "--output_dir",
        type=str,
        default="./tmp/"
    )

    args = parser.parse_args()

    dataset = load_train_data(args.data_path)

    print(dataset)

    model = SentenceTransformer(args.model_path)

    loss = TripletLoss(model)

    training_args = SentenceTransformerTrainingArguments(
        output_dir=args.output_dir,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        eval_strategy="steps",
        save_strategy="epoch",
        logging_steps=50,
        eval_steps=100,
        warmup_ratio=0.1,
        fp16=True,
        remove_unused_columns=False,
        save_total_limit=1,
    )

    trainer = SentenceTransformerTrainer(
        model=model,
        args=training_args,
        train_dataset=dataset["train"],
        eval_dataset=dataset["validation"],
        loss=loss,
    )

    trainer.train()

    model.save_pretrained(args.output_dir)
