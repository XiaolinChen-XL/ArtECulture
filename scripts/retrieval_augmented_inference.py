"""Run two-stage retrieval and knowledge-conditioned emotion inference."""

import argparse

from common import append_jsonl, call_chat, iter_jsonl
from prompts import RETRIEVAL_PROMPTS


def retrieve(query, entries, encoder, threshold):
    """Use exact matching first, then semantic matching above a threshold."""
    exact = next((entry for entry in entries if entry["concept"].casefold() == query.casefold()), None)
    if exact is not None:
        return exact
    if not entries:
        return None
    vectors = encoder.encode([query] + [entry["concept"] for entry in entries], normalize_embeddings=True)
    scores = vectors[1:] @ vectors[0]
    index = int(scores.argmax())
    return entries[index] if float(scores[index]) >= threshold else None


def format_knowledge(entries):
    """Serialize retrieved culture-specific tuples for prompt injection."""
    return "\n".join(
        f"- concept: {entry['concept']}; emotion: {entry['dominant_emotion']}; "
        f"rationales: {' | '.join(entry['rationales'])}"
        for entry in entries
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="JSONL with image_path, culture, and concepts.")
    parser.add_argument("--knowledge-base", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--embedding-model", required=True)
    parser.add_argument("--threshold", type=float, default=0.85)
    parser.add_argument("--max-tuples", type=int, default=5)
    parser.add_argument("--endpoint", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--api-key-env", default=None)
    args = parser.parse_args()

    from sentence_transformers import SentenceTransformer

    encoder = SentenceTransformer(args.embedding_model)
    knowledge = list(iter_jsonl(args.knowledge_base))
    for record in iter_jsonl(args.input):
        culture_entries = [entry for entry in knowledge if entry["culture"] == record["culture"]]
        retrieved = []
        for concept in record["concepts"]:
            match = retrieve(concept, culture_entries, encoder, args.threshold)
            if match is not None and match not in retrieved:
                retrieved.append(match)
                if len(retrieved) >= args.max_tuples:
                    break
        prompt = RETRIEVAL_PROMPTS[record["culture"]].format(
            retrieved_tuples=format_knowledge(retrieved),
        )
        response = call_chat(
            args.endpoint, args.model, prompt, record["image_path"], args.api_key_env,
        )
        append_jsonl(args.output, {**record, "retrieved_tuples": retrieved, "response": response})


if __name__ == "__main__":
    main()
