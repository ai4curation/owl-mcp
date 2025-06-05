def guess_serialization(file_path: str) -> str | None:
    if file_path.endswith(".owl"):
        with open(file_path) as f:
            first_line = f.readline()
            if first_line.startswith(("Prefix(", "Ontology(")):
                return "ofn"
            return None
    return None
