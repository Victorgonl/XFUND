import os
import json
import zipfile


XFUND_URL = "https://github.com/doc-analysis/XFUND/releases/download/v1.0/"
DOWNLOAD_FOLDER = "./xfund_original/"
XFUND_FOLDER = "./xfund/"
XFUND_DATA_FOLDER = f"{XFUND_FOLDER}data/"
XFUND_IMAGE_FOLDER = f"{XFUND_FOLDER}image/"
XFUND_LANGUAGES = ["zh", "de", "es", "fr", "it", "ja", "pt"]
XFUND_CITATION_FILE = "./xfund.bib"


def download_file(url, download_directory):
    os.system(f"wget -c {url} -P {download_directory}")


def extract_data_from_json(data_file_directory):
    data = {}
    with open(data_file_directory, "r") as data_file:
        json_data = json.load(data_file)
    for document in json_data["documents"]:
        sample = []
        for document_entitie in document["document"]:
            entitie = {"id": document_entitie["id"],
                "text": document_entitie["id"],
                    "text": document_entitie["text"],
                    "box": document_entitie["box"],
                    "label": document_entitie["label"].upper(),
                    "words": [],
                    "boxes": [],
                    "link": document_entitie["linking"]}
            for word_box in document_entitie["words"]:
                word = word_box["text"]
                box = word_box["box"]
                entitie["words"].append(word)
                entitie["boxes"].append(box)
            sample.append(entitie)
        data[document["id"]] = sample
    return data

def extract_zip(zip_directory, extract_directory):
    with zipfile.ZipFile(zip_directory, 'r') as zip_ref:
        zip_ref.extractall(extract_directory)


def save_data(data, data_directory):
    for sample_key in data.keys():
        with open(f"{data_directory}/{sample_key}.json", "w") as json_data:
            json.dump(data[sample_key], json_data, indent=4)


def xfund(languages=XFUND_LANGUAGES):
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
    os.makedirs(XFUND_DATA_FOLDER, exist_ok=True)
    xfund_info = {"name": "XFUND",
                  "split": {},
                  "citation": None}
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
        xfund_info["split"][language] = {"train": [],
                            "val": []}
        for train_sample_key in train_data.keys():
            xfund_info["split"][language]["train"].append(train_sample_key)
        for val_sample_key in val_data.keys():
            xfund_info["split"][language]["val"].append(val_sample_key)
    with open(f"{XFUND_FOLDER}/xfund.json", "w") as xfund_info_json:
        json.dump(xfund_info, xfund_info_json, indent=4)


if __name__ == '__main__':
    xfund()