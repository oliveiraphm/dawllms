from dotenv import load_dotenv
import openai
import os
import argparse
import pandas as pd
import time
from sklearn.cluster import KMeans


load_dotenv(dotenv_path="../.env")

OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")

client = openai.OpenAI()

def get_embedding(text):
    
    for nr_retries in range(1, 4):
        try:
            response = client.embeddings.create(
                model = 'text-embedding-ada-002',
                input = text
            )
            return response.data[0].embedding
        except:
            time.sleep(nr_retries * 2)
    raise Exception('Cannot query OpenAI model!')

def get_kmeans(embeddings, k):

    kmeans = KMeans(n_clusters=k, int='k-means++')
    kmeans.fit(embeddings)
    return kmeans.labels_

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('file_path', type=str, help='Path to input file')
    parser.add_argument('nr_clusters', type=int, help='Number of clusters')
    args = parser.parse_args()

    df = pd.read_csv(args.file_path)

    embeddings = df['text'].apply(get_embedding)
    df['clusterid'] = get_kmeans(list(embeddings), args.nr_clusters)

    df.to_csv('result.csv')