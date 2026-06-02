import os
import json
import argparse
import torch
import pandas as pd

from tqdm import tqdm
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from torch.utils.data import DataLoader

MAX_TEXT_LENGTH = 512


# =====================================================
# ARGUMENTS
# =====================================================

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--max_length",
        type=int,
        default=512,
        help="Max length khi generate"
    )

    parser.add_argument(
        "--model_path",
        type=str,
        required=True,
        help="Directory chứa checkpoint"
    )

    parser.add_argument(
        "--test_data_path",
        type=str,
        required=True,
        help="File test json"
    )

    parser.add_argument(
        "--batch_size",
        type=int,
        default=32
    )

    parser.add_argument(
        "--output_file",
        type=str,
        default="prediction_results.json"
    )

    return parser.parse_args()


# =====================================================
# DATA
# =====================================================

def prepare_features(example):
    tokenizer = prepare_features.tokenizer

    features = {
        "source_ids": [],
        "source_mask": [],
        "target_ids": []
    }

    total = len(example["input"])

    for i in range(total):

        source = tokenizer(
            example["input"][i],
            max_length=MAX_TEXT_LENGTH,
            truncation=True
        )

        target = tokenizer(
            example["target"][i],
            max_length=MAX_TEXT_LENGTH,
            truncation=True
        )

        features["source_ids"].append(source["input_ids"])
        features["source_mask"].append(source["attention_mask"])
        features["target_ids"].append(target["input_ids"])

    return features


def pad_to_maxlen(input_ids, max_len, pad_value=0):
    if len(input_ids) >= max_len:
        return input_ids[:max_len]

    return input_ids + [pad_value] * (max_len - len(input_ids))


def test_collate_fn(batch):

    max_len = max(len(x["source_ids"]) for x in batch)

    source_ids = []
    source_mask = []
    target_ids = []

    for item in batch:

        source_ids.append(
            pad_to_maxlen(item["source_ids"], max_len)
        )

        source_mask.append(
            pad_to_maxlen(item["source_mask"], max_len)
        )

        target_ids.append(item["target_ids"])

    return {
        "source_ids": torch.tensor(source_ids),
        "source_mask": torch.tensor(source_mask),
        "target_ids": target_ids
    }


# =====================================================
# METRIC
# =====================================================

def split2pair(answer, text):

    res = []

    if len(answer) < 2:
        return []

    answer = answer[1:-1]

    left, right = 0, 0

    while right < len(answer):

        if answer[right] == "(":
            left = right + 1

        elif answer[right] == ")":

            comma_index = answer[left:right].find(",")

            if comma_index == -1:
                right += 1
                continue

            t = [
                answer[left:right][:comma_index].strip(),
                answer[left:right][comma_index + 1:].strip()
            ]

            res.append((t[0], t[1]))

        right += 1

    return list(set(res))


# =====================================================
# MAIN
# =====================================================

def main():

    args = parse_args()
    MAX_TEXT_LENGTH = args.max_length

    device = "cuda" if torch.cuda.is_available() else "cpu"

    print(f"Using device: {device}")

    tokenizer = AutoTokenizer.from_pretrained(
        args.model_path,
        trust_remote_code=True
    )

    model = AutoModelForSeq2SeqLM.from_pretrained(
        args.model_path,
        trust_remote_code=True
    )

    state_dict = torch.load(
        os.path.join(args.model_path, "pytorch_model.bin"),
        map_location=device
    )

    model.load_state_dict(
        state_dict,
        strict=False
    )

    model.to(device)
    model.eval()

    print("Loaded model:", args.model_path)

    # ----------------------------
    # dataset
    # ----------------------------

    prepare_features.tokenizer = tokenizer

    dataset = load_dataset(
        "json",
        data_files=args.test_data_path,
        split="train"
    )

    raw_inputs = dataset["input"]
    raw_targets = dataset["target"]

    dataset = dataset.map(
        prepare_features,
        batched=True
    )

    dataloader = DataLoader(
        dataset,
        batch_size=args.batch_size,
        shuffle=False,
        collate_fn=test_collate_fn
    )

    # ----------------------------
    # predict
    # ----------------------------

    all_pred_text = []
    all_gt_text = []
    all_input_text = []

    sample_idx = 0

    with torch.no_grad():

        for batch in tqdm(dataloader):

            ids = batch["source_ids"].to(device)
            mask = batch["source_mask"].to(device)

            generated_ids = model.generate(
                input_ids=ids,
                attention_mask=mask,
                max_length=MAX_TEXT_LENGTH // 2
            )

            pred_texts = tokenizer.batch_decode(
                generated_ids,
                skip_special_tokens=True
            )

            bs = len(pred_texts)

            for i in range(bs):

                all_pred_text.append(pred_texts[i])
                all_gt_text.append(raw_targets[sample_idx])
                all_input_text.append(raw_inputs[sample_idx])

                sample_idx += 1

    # ----------------------------
    # metric
    # ----------------------------

    nb_correct = 0
    nb_pred = 0
    nb_label = 0

    records = []

    for inp, pred_text, gt_text in zip(
        all_input_text,
        all_pred_text,
        all_gt_text
    ):

        pred_pairs = split2pair(pred_text, inp)
        gt_pairs = split2pair(gt_text, inp)

        nb_pred += len(pred_pairs)
        nb_label += len(gt_pairs)

        for pair in pred_pairs:
            if pair in gt_pairs:
                nb_correct += 1

        records.append({
            "input": inp,
            "predict_text": pred_text,
            "ground_truth_text": gt_text,
            "predict_pairs": pred_pairs,
            "ground_truth_pairs": gt_pairs
        })

    precision = nb_correct / nb_pred if nb_pred else 0
    recall = nb_correct / nb_label if nb_label else 0

    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall
        else 0
    )

    print()
    print("=" * 50)
    print(f"nb_pred    : {nb_pred}")
    print(f"nb_label   : {nb_label}")
    print(f"nb_correct : {nb_correct}")
    print()
    print(f"Precision : {precision:.6f}")
    print(f"Recall    : {recall:.6f}")
    print(f"F1        : {f1:.6f}")
    print("=" * 50)

    output = {
        "metrics": {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "nb_pred": nb_pred,
            "nb_label": nb_label,
            "nb_correct": nb_correct
        },
        "predictions": records
    }

    with open(
        args.output_file,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            output,
            f,
            ensure_ascii=False,
            indent=2
        )

    print(f"Saved to {args.output_file}")


if __name__ == "__main__":
    main()