def guess_serialization(file_path: str) -> str | None:
    if file_path.endswith(".owl"):
        with open(file_path, "r") as f:
            first_line = f.readline()
            if first_line.startswith("Prefix(") or first_line.startswith("Ontology("):
                return "ofn"
            return None
