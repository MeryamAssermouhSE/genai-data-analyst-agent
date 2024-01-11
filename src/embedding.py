import vertexai
from vertexai.preview.language_models import TextEmbeddingModel
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def get_text_embeddings(texts, model_name="textembedding-gecko@001", chunk_size=200):
    """Get text embeddings using the Vertex AI Text Embedding API. Splits input vector into chunks with 200 elements each for efficient processing."""
    client = TextEmbeddingModel.from_pretrained(model_name)
    embeddings_values = []
    for i in range(0, len(texts), chunk_size):
        chunk = texts[i:i + chunk_size]
        embeddings = client.get_embeddings(chunk)
        for embedding in embeddings:
            embeddings_values.append(embedding.values)
    return embeddings_values
def find_most_similar_vector(vectors_list, target_vector):
    similarities = [cosine_similarity([target_vector], [vector])[0][0] for vector in vectors_list]
    most_similar_index = np.argmax(similarities)
    return most_similar_index


if __name__=="__main__":
    l = ['word', 'sentence', 'world','input','output','is it true']
    target = ['Word']
    l = get_text_embeddings(l)
    print(len(l))
    target = get_text_embeddings(target)[0]
    i = find_most_similar_vector(l,target)
    print(i)
