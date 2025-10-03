# some helper functions for visualizing and clustering HGV text classes
import json
import random
from typing import List, Tuple 
from collections import Counter
import spacy
from sklearn.metrics.pairwise import cosine_distances
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.manifold import TSNE
from thinc.types import Floats1d
import numpy as np
import matplotlib.pyplot as plt
from mplcursors import cursor

def get_embeddings(word_classes: List[str], model: str = "de_core_news_lg") -> List[Tuple[str, Floats1d, int]]:
    # Get word embedding for word classes, but in case there are multiple words take the first noun.
    # When there are no nouns, just take the first word's vector
    print("Loading NLP model...")
    nlp = spacy.load(model)
   
    word_classes_counter = Counter(word_classes)

    print("Computing embeddings...")
    # This list uses more memory than strictly necessary by holding on to the embeddings.
    # If I don't, they have to be recomputed at the end of this function, which I deem more resource-intensive.
    word_classes_with_count_embedding_and_token: List[Tuple[str, int, str, Floats1d]] = []
    for doc in nlp.pipe(set(word_classes), disable=["ner", "parser", "attribute_ruler", "lemmatizer"]):
        for token in doc:
            if not token.has_vector:
                continue
            if token.pos_ == "NOUN":
                word_classes_with_count_embedding_and_token.append((str(doc), word_classes_counter[str(doc)], str(token), token.vector))
                break
        else:
            # If there was no noun, just use the first token that has a vector
            for token in doc:
                if token.has_vector:
                    word_classes_with_count_embedding_and_token.append((str(doc), word_classes_counter[str(doc)], str(doc[0]), doc[0].vector))
            # If we don't find a token with a vector, quietly continue

    # Collect only one result for every token, and with it collect the most common word class as an example.
    # If there are multiple of the same token (and embedding) this isn't very useful and makes clustering and TSNE behave worse.
    # Loop over all the results and keep track of every token, an example for it and the times this example occurs in the list
    # Replace the example if a higher-count one is found.
    results_dict: dict[str, Tuple[str, int, Floats1d]] = {}

    for word_class, count, token, embedding in word_classes_with_count_embedding_and_token:
        if (result := results_dict.get(token)) is not None and result[1] > count:
            # if there is already a token with a better example (higher count) continue with the rest of the list
            continue
        results_dict[token] = (word_class, count, embedding)
    
    results = [(example, embedding, _) for _, (example, _, embedding) in results_dict.items()] 
    return results
       
def compute_clusters(words_and_embeddings: List[Tuple[str, Floats1d, int]], n_clusters: int) -> List[Tuple[int, str, Floats1d, int]]:
    words, embeddings, counts = zip(*words_and_embeddings)
    print("Calculating distance matrix...")
    distance_matrix = cosine_distances(embeddings)
    # TODO improve clustering algorithm?
    clustering = KMeans(
       n_clusters=n_clusters,
    )
    print("Computing clusters...")
    labels= clustering.fit_predict(distance_matrix)
    
    clusters = []
    for label, word, embedding, count in zip(labels, words, embeddings, counts):
        clusters.append((label, word, embedding, count))
    return clusters

def visualize(clusters: List[Tuple[int, str, Floats1d, int]], limit: int = 5000, num_labelled: int = 50):
    if len(clusters) > limit:
        clusters = random.sample(clusters, limit)

    print("Running TSNE...")
    tsne = TSNE(random_state=37, perplexity=5)
    labels, words, embeddings, counts = zip(*clusters)
    embeddings_tsne = tsne.fit_transform(np.array(embeddings))
    
    

    num_clusters = len(set(labels))
    colors = [f"#{random.randrange(0x1000000):06x}" for _ in range(num_clusters)]
    final_clusters = list(zip(labels, embeddings_tsne, words, counts))
    
    final_clusters.sort(key=lambda x: x[3], reverse=True)
    cluster_labels = {}
    for label in set(labels):
        example_for_legend = next(clustered_word[2] for clustered_word in final_clusters if clustered_word[0] == label)
        cluster_labels[label] = f"{example_for_legend} - {label}"
    

    for label, (x,y), word, _ in final_clusters:
        plt.scatter(x,y, color=colors[label % len(colors)], label=cluster_labels[label])
    
    if num_labelled > len(words):
        num_labelled = len(words)
    
    for _, (x,y), word, _ in random.sample(final_clusters, num_labelled):
        plt.text(x, y, word)
    
    legend_without_duplicate_labels(plt)
    cursor(hover=True)
    plt.show()

# https://stackoverflow.com/questions/19385639/duplicate-items-in-legend-in-matplotlib
def legend_without_duplicate_labels(figure):
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    figure.legend(by_label.values(), by_label.keys())

def visualize_word_class_clusters(word_classes: List[str], num_clusters: int, visualize_limit: int, num_labels: int):
    embeddings = get_embeddings(word_classes)
    clusters = compute_clusters(embeddings, num_clusters)
    visualize(clusters, visualize_limit, num_labels)

if __name__=="__main__":
    # run a few tests
    embeddings = get_embeddings(["zwei", "drei", "vier", "Montag", "Dienstag", "Mittwoch", "Ich bin ein Apfel"])
    print([e[0] for e in embeddings])
    clusters = compute_clusters(embeddings, 3)
    clusters.sort(key=lambda x: x[0])
    for cluster, word, _, _ in clusters:
        print(f"{cluster}: {word}")
    visualize(clusters)
