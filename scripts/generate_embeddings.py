import os
from dotenv import load_dotenv
from supabase import create_client, Client
from openai import OpenAI
import numpy as np

# Load environment variables from .env file
load_dotenv()

# Get Supabase and OpenAI credentials from environment variables
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Check for missing credentials
if not all([SUPABASE_URL, SUPABASE_SERVICE_KEY, OPENAI_API_KEY]):
    raise ValueError("Missing required environment variables: SUPABASE_URL, SUPABASE_SERVICE_KEY, OPENAI_API_KEY")

# Configuration for the embedding process
BATCH_SIZE = 100
EMBEDDING_MODEL = "text-embedding-3-small"
TABLE_NAME = "tags_final"  # Ensure this matches your table name

# Initialize Supabase and OpenAI clients
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def get_embedding(text: str, model: str = EMBEDDING_MODEL) -> list[float]:
    """
    Generates an embedding for the given text using the specified OpenAI model.
    """
    # Replace newlines with spaces, as recommended by OpenAI for better embeddings
    text = text.replace("\n", " ")
    response = openai_client.embeddings.create(input=[text], model=model)
    return response.data[0].embedding

def main():
    """
    Main function to process tags in batches, generate embeddings, and update the database.
    """
    print("Starting the embedding generation process...")

    processed_count = 0
    while True:
        try:
            # Fetch a batch of tags that do not have an embedding yet
            response = supabase.table(TABLE_NAME).select('id, name').is_('embedding', 'null').limit(BATCH_SIZE).execute()
            tags_to_process = response.data

            if not tags_to_process:
                print("All tags have been processed. Exiting.")
                break

            print(f"Processing a batch of {len(tags_to_process)} tags...")

            # Prepare tag names for the embedding API
            tag_names = [tag['name'] for tag in tags_to_process]

            # Generate embeddings for the batch of tag names
            embeddings = [get_embedding(name, model=EMBEDDING_MODEL) for name in tag_names]

            # Prepare the data for upserting back into Supabase
            updates = [
                {'id': tag['id'], 'embedding': np.array(embeddings[i]).tolist()}
                for i, tag in enumerate(tags_to_process)
            ]

            # Upsert the embeddings into the database
            supabase.table(TABLE_NAME).upsert(updates).execute()

            processed_count += len(tags_to_process)
            print(f"Successfully processed batch. Total tags processed so far: {processed_count}")

        except Exception as e:
            print(f"An error occurred: {e}")
            print("Stopping the process due to an error.")
            break

if __name__ == "__main__":
    main()
