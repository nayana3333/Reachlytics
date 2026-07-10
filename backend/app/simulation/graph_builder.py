import random

import networkx as nx


def build_social_graph(personas: list[dict], seed: int = 42) -> nx.Graph:
    random.seed(seed)
    count = len(personas)
    k = min(8, max(4, count // 18))
    graph = nx.watts_strogatz_graph(count, k, 0.22, seed=seed)

    for index, persona in enumerate(personas):
        graph.nodes[index].update(persona)

    for source, target in graph.edges:
        source_persona = personas[source]
        target_persona = personas[target]
        shared = len(set(source_persona["interests"]).intersection(target_persona["interests"]))
        similarity = min(1.0, 0.25 + shared * 0.2)
        if source_persona["in_target"] == target_persona["in_target"]:
            similarity += 0.15
        graph.edges[source, target]["interest_similarity"] = min(1.0, similarity)
        graph.edges[source, target]["relationship_strength"] = round(random.uniform(0.25, 0.95), 2)

    return graph
