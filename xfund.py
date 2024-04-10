import os
import json
import zipfile
import pathlib
import sys

from utils.sort import sort_samples_data
from utils.sort import UflaFormsJSONEncoder


ROOT_PATH = pathlib.Path(__file__).parent.resolve()
XFUND_URL = "https://github.com/Victorgonl/XFUND/releases/download/v1.0/"
DOWNLOAD_FOLDER = f"{ROOT_PATH}/xfund_original/"
XFUND_FOLDER = f"{ROOT_PATH}/xfund/"
XFUND_DATA_FOLDER = f"{XFUND_FOLDER}data/"
XFUND_IMAGE_FOLDER = f"{XFUND_FOLDER}image/"
XFUND_CITATION_FILE = f"{ROOT_PATH}/xfund.bib"
XFUND_LANGUAGES = ["zh", "de", "es", "fr", "it", "ja", "pt"]
XFUND_LANGUAGES = ["pt"]

INFO_NAME = "dataset_name"
INFO_SPLITS = "splits"
INFO_CITATION = "citation"

DATASET_INFO_FILE = "dataset_info.json"


def download_file(url, download_directory):
    os.system(f"wget -c {url} -P {download_directory}")


def extract_data_from_json(data_file_directory):
    data = {}
    with open(data_file_directory, "r") as data_file:
        json_data = json.load(data_file)
    for document in json_data["documents"]:
        sample = []
        for document_entitie in document["document"]:
            entity = {"id": document_entitie["id"],
                "text": document_entitie["id"],
                    "text": document_entitie["text"],
                    "box": document_entitie["box"],
                    "label": document_entitie["label"].upper(),
                    "words": [],
                    "boxes": [],
                    "links": document_entitie["linking"]}
            for word_box in document_entitie["words"]:
                word = word_box["text"]
                box = word_box["box"]
                entity["words"].append(word)
                entity["boxes"].append(box)
            sample.append(entity)
        data[document["id"]] = sample
    data = sort_samples_data(data, sort_by_relations=True)
    return data

def extract_zip(zip_directory, extract_directory):
    with zipfile.ZipFile(zip_directory, 'r') as zip_ref:
        zip_ref.extractall(extract_directory)


def save_data(data, data_directory):
    for sample_key in data.keys():
        with open(f"{data_directory}/{sample_key}.json", "w") as json_data:
            json.dump(data[sample_key], json_data, indent=4)


def xfund(languages=XFUND_LANGUAGES):
    if not all(language in XFUND_LANGUAGES for language in languages):
        raise Exception(f"Language(s) not available on XFUND. Try these {XFUND_LANGUAGES}.")
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
    os.makedirs(XFUND_DATA_FOLDER, exist_ok=True)
    xfund_info = {INFO_NAME: "XFUND",
                  INFO_SPLITS: {},
                  INFO_CITATION: None}
    with open(XFUND_CITATION_FILE, "r") as xfund_citation:
        xfund_info["citation"] = xfund_citation.read()
    for language in languages:
        # train samples
        train_json_file = f"{language}.train.json"
        train_zip_file = f"{language}.train.zip"
        download_file(f"{XFUND_URL}/{train_json_file}", DOWNLOAD_FOLDER)
        download_file(f"{XFUND_URL}/{train_zip_file}", DOWNLOAD_FOLDER)
        train_data = extract_data_from_json(f"{DOWNLOAD_FOLDER}/{train_json_file}")
        save_data(train_data, XFUND_DATA_FOLDER)
        extract_zip(f"{DOWNLOAD_FOLDER}/{train_zip_file}", XFUND_IMAGE_FOLDER)
        # validation samples
        val_json_file = f"{language}.val.json"
        val_zip_file = f"{language}.val.zip"
        download_file(f"{XFUND_URL}/{val_json_file}", DOWNLOAD_FOLDER)
        download_file(f"{XFUND_URL}/{val_zip_file}", DOWNLOAD_FOLDER)
        val_data = extract_data_from_json(f"{DOWNLOAD_FOLDER}/{val_json_file}")
        save_data(val_data, XFUND_DATA_FOLDER)
        extract_zip(f"{DOWNLOAD_FOLDER}/{val_zip_file}", XFUND_IMAGE_FOLDER)
         # splits
        xfund_info[INFO_SPLITS] = {"train": [],
                            "val": []}
        for train_sample_key in train_data.keys():
            xfund_info[INFO_SPLITS]["train"].append(train_sample_key)
        for val_sample_key in val_data.keys():
            xfund_info[INFO_SPLITS]["val"].append(val_sample_key)
    with open(f"{XFUND_FOLDER}/{DATASET_INFO_FILE}", "w") as xfund_info_json:
        json.dump(xfund_info, xfund_info_json, cls=UflaFormsJSONEncoder, indent=4)


if __name__ == '__main__':
    languages_to_load = sys.argv[1:]
    xfund(languages=languages_to_load) if len(languages_to_load) else xfund()