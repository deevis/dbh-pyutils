# Initially borrowed from oobabooga's superbooga extension!
import chromadb
import posthog
import torch
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import time
import logging

posthog.capture = lambda *args, **kwargs: None


class Collecter():
    def __init__(self):
        pass

    def add(self, texts: list[str]):
        pass

    def get(self, search_strings: list[str], n_results: int) -> list[str]:
        pass

    def clear(self):
        pass


class Embedder():
    def __init__(self):
        pass

    def embed(self, text: str) -> list[torch.Tensor]:
        pass


class ChromaCollector(Collecter):
    def __init__(self, embedder, collection_name: str, persist_directory: str = "chromadb"):
        super().__init__()
        self.chroma_client = chromadb.PersistentClient(path=persist_directory,
                                                       settings=Settings(anonymized_telemetry=False))
        self.embedder = embedder
        self.set_collection(collection_name)

    def set_collection(self, collection_name: str):
        self.collection_name = collection_name
        print(f'ChromaDB using collection: {collection_name}')
        self.collection = self.chroma_client.get_or_create_collection(name=collection_name, 
                                                                      embedding_function=self.embedder)

    def add(self, documents: list[str], metadata: list[dict[str, str]], ids: list[str]):
        if len(documents) == 0:
            return
        print(f"Adding {len(documents)} documents to chromadb")
        start = time.time()
        self.collection.add(documents=documents, metadatas=metadata, ids=ids)
        print(f"Added {len(documents)} documents to chromadb in {time.time() - start} seconds")

    # Get chunks by similarity
    def get(self, search_strings: list[str], n_results: int) -> list[str]:
        documents, ids, distances, metadatas = self.get_documents_ids_distances(search_strings, n_results)
        return documents, ids, distances, metadatas

    def get_documents_ids_distances(self, search_strings: list[str], n_results=5):
        # n_results = min(len(self.ids), n_results)
        if n_results == 0:
            return [], [], []

        result = self.collection.query(query_texts=search_strings, n_results=n_results, include=['documents', 'distances','metadatas'])
        # print(f'Result[documents]: {result["documents"]}')
        # print(f'Result[ids]: {result["ids"]}')
        # print(f'Result[distances]: {result["distances"]}')
        # print(f'Result[metadatas]: {result["metadatas"]}')
        documents = result['documents'][0]
        ids = result['ids'][0]
        distances = result['distances'][0]
        metadatas = result['metadatas'][0]
        return documents, ids, distances, metadatas


    # Get ids by similarity
    def get_ids(self, search_strings: list[str], n_results: int) -> list[str]:
        _, ids, _, _ = self.get_documents_ids_distances(search_strings, n_results)
        return ids

    # Get chunks by similarity and then sort by insertion order
    def get_sorted(self, search_strings: list[str], n_results: int) -> list[str]:
        documents, ids, _, metadatas = self.get_documents_ids_distances(search_strings, n_results)
        return [x for _, x in sorted(zip(ids, documents))]

    # Get ids by similarity and then sort by insertion order
    def get_ids_sorted(self, search_strings: list[str], n_results: int, n_initial: int = None, time_weight: float = 1.0) -> list[str]:
        do_time_weight = time_weight > 0
        if not (do_time_weight and n_initial is not None):
            n_initial = n_results
        elif n_initial == -1:
            n_initial = self.collection.count()

        if n_initial < n_results:
            raise ValueError(f"n_initial {n_initial} should be >= n_results {n_results}")

        _, ids, distances = self.get_documents_ids_distances(search_strings, n_initial)
        if do_time_weight:
            distances_w = self.apply_time_weight_to_distances(ids, distances, time_weight=time_weight)
            results = zip(ids, distances, distances_w)
            results = sorted(results, key=lambda x: x[2])[:n_results]
            results = sorted(results, key=lambda x: x[0])
            ids = [x[0] for x in results]

        return sorted(ids)

    def clear(self):
        self.chroma_client.delete_collection(name=self.collection_name)
        self.set_collection(collection_name=self.collection_name)

# was make_collector
def make_chroma_collector(collection_name: str, embedder = None, persist_directory: str = "chromadb", overwrite: bool = False):
    if embedder is None:
        embedder = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

    collector = ChromaCollector(embedder, collection_name=collection_name, persist_directory=persist_directory)
    print(f'ChromaDB[{persist_directory}] using collection: {collection_name}')
    if overwrite:
        print(f'Overwriting ChromaDB collection: {collection_name}')
        collector.clear()
    return collector


def add_chunks_to_collector(chunks, collector):
    collector.clear()
    collector.add(chunks)


