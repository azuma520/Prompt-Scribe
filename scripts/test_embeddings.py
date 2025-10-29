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
BATCH_SIZE = 5  # Small batch for testing
EMBEDDING_MODEL = "text-embedding-3-small"
TABLE_NAME = "tags_final"

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
    Test function to process a small batch of tags for embedding generation.
    """
    print("Starting the embedding generation test...")
    print(f"Supabase URL: {SUPABASE_URL}")
    print(f"Service Key: {'Set' if SUPABASE_SERVICE_KEY else 'Not Set'}")
    print(f"OpenAI Key: {'Set' if OPENAI_API_KEY else 'Not Set'}")

    try:
        # Fetch a small batch of tags that do not have an embedding yet
        response = supabase.table(TABLE_NAME).select('id, name').is_('embedding', 'null').limit(BATCH_SIZE).execute()
        tags_to_process = response.data

        if not tags_to_process:
            print("All tags have been processed. Exiting.")
            return

        print(f"Processing a batch of {len(tags_to_process)} tags...")
        for tag in tags_to_process:
            print(f"  - {tag['name']} (ID: {tag['id']})")

        # Prepare tag names for the embedding API
        tag_names = [tag['name'] for tag in tags_to_process]

        # Generate embeddings for the batch of tag names
        print("Generating embeddings...")
        embeddings = []
        for i, name in enumerate(tag_names):
            print(f"  Processing {i+1}/{len(tag_names)}: {name}")
            embedding = get_embedding(name, model=EMBEDDING_MODEL)
            embeddings.append(embedding)
            print(f"    Generated embedding with {len(embedding)} dimensions")

        # Prepare the data for upserting back into Supabase
        updates = [
            {'id': tag['id'], 'embedding': np.array(embeddings[i]).tolist()}
            for i, tag in enumerate(tags_to_process)
        ]

        # Upsert the embeddings into the database
        print("Updating database...")
        supabase.table(TABLE_NAME).upsert(updates).execute()

        print(f"Successfully processed {len(tags_to_process)} tags!")

    except Exception as e:
        print(f"An error occurred: {e}")
        print("Stopping the process due to an error.")
        raise

if __name__ == "__main__":
    main()

