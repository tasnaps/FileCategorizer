def build_prompt(csv_prompt, file_key, candidate_labels_with_descriptions):
    """
    Build a classification prompt that includes CSV metadata,
    the file key, and a list of candidate genres with descriptions.
    """
    # Introductory context
    context = (
        "You are a literary classifier. Based on the given book metadata, "
        "please determine the most appropriate genre from the following candidates. "
        "If the metadata indicates that the book is a language textbook, educational material, "
        "or any category not explicitly listed, please assign it to 'Other'.\n\n"
    )

    labels_info = "\n".join([f"{label}: {desc}"
                             for label, desc in candidate_labels_with_descriptions.items()])
    # Combine all elements: context, csv metadata, file key, and candidate genre details.
    prompt = f"{context}{csv_prompt} {file_key}\nCandidate Genres:\n{labels_info}"
    return prompt
