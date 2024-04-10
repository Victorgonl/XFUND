import copy

KEYS_ORDER = ["id", "text", "box", "words", "boxes", "label", "links"]


def get_entities_indexes_by_dfs(relations):

    # save values for skiping
    values = set()
    for entity in relations:
        for value in relations[entity]:
            if value not in values:
                values.add(value)

    sorted_entities = []

    def dfs(entity):
        if entity in sorted_entities:
            return
        sorted_entities.append(entity)
        for next_entity in relations[entity]:
            dfs(next_entity)

    for entity in relations:
        if entity not in values:
            dfs(entity)

    return sorted_entities


def extract_adjacency_dict(entities):
    adjacency_dict = {}
    links = []

    for entity in entities:
        adjacency_dict[entity["id"]] = []
        for link in entity["links"]:
            if link not in links:
                links.append(link)

    for entity_id in adjacency_dict:
        for link in links:
            if link[0] == entity_id:
                adjacency_dict[entity_id].append(link[1])

    """ adjacency_dict = {
        k: adjacency_dict[k] for k in sorted(adjacency_dict, reverse=True)
    } """

    return adjacency_dict


def sort_entities_by_relations(entities):
    """Sort entities by their relations graph."""
    adjacency_dict = extract_adjacency_dict(entities)
    sorted_entities = get_entities_indexes_by_dfs(adjacency_dict)
    new_entities = []
    entities = {entity["id"]: entity for entity in entities}
    for entity_id in sorted_entities:
        new_entities.append(entities[entity_id])
    make_entities_ids_sequencial(new_entities)
    return new_entities


def sort_entities_by_position(entities):
    """Sort the entities passed by book position, from top to bottom and left to right."""

    entities.sort(
        key=lambda entity: (
            entity["box"][1],
            entity["box"][0],
            entity["box"][3],
            entity["box"][2],
            entity["id"],
        )
    )


def sort_entities_links(entities):
    for entity in entities:
        entity["links"].sort(key=lambda link: (link[0], link[1]))


def make_entities_ids_sequencial(entities):
    def fix_links_ids(entities, ids_map):
        for entity in entities:
            for link in entity["links"]:
                link[0] = ids_map[link[0]]
                link[1] = ids_map[link[1]]

    def create_invalid_ids(entities):
        ids_map = {}
        for entity in entities:
            ids_map[entity["id"]] = entity["id"] * -1
            entity["id"] = ids_map[entity["id"]]
        fix_links_ids(entities, ids_map)

    create_invalid_ids(entities)
    ids_map = {}
    for i, entity in enumerate(entities):
        ids_map[entity["id"]] = i
        entity["id"] = ids_map[entity["id"]]
    fix_links_ids(entities, ids_map)
    sort_entities_links(entities)


def sort_samples_data(samples_data, sort_by_relations=False):
    samples_data = copy.deepcopy(samples_data)
    sorted_samples_data = {}

    for sample_id in samples_data:

        # sort sample
        sample = samples_data[sample_id]
        sort_entities_by_position(sample)
        make_entities_ids_sequencial(sample)
        if sort_by_relations:
            sample = sort_entities_by_relations(sample)

        # sort sample entities keys
        sorted_sample = []
        for entity in sample:
            sorted_entity = {}
            for key in KEYS_ORDER:
                sorted_entity[key] = entity[key]
            sorted_sample.append(sorted_entity)
        sorted_samples_data[sample_id] = sorted_sample

    return sorted_samples_data


if __name__ == "__main__":

    import os
    import json

    from json_encoder import UflaFormsJSONEncoder

    def load_samples_data(data_folder):
        samples_data = {}
        for data_file in sorted(os.listdir(data_folder)):
            sample_id = data_file.split(".json")[0]
            data_path = os.path.join(data_folder, data_file)
            if os.path.isfile(data_path):
                data = json.load(open(data_path))
                samples_data[sample_id] = data
        return samples_data

    def save_samples_data(data_folder, samples_data):
        for sample_id in samples_data:
            with open(f"{data_folder}/{sample_id}.json", "w") as f:
                json.dump(samples_data[sample_id], f, cls=UflaFormsJSONEncoder, indent=4)

    data_folder = "./xfund/data/"

    samples_data = load_samples_data(data_folder=data_folder)
    samples_data = sort_samples_data(samples_data=samples_data, sort_by_relations=True)
    save_samples_data(data_folder=data_folder, samples_data=samples_data)

    print()
    print("========================")
    print("|| UFLA-FORMS sorted! ||")
    print("========================")
    print()
