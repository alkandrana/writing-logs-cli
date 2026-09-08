
def split_compound_id(compound_id: str) -> dict[str, str]:
    codes = {}
    if "-" in compound_id:
        parts = compound_id.split("-")
        codes["project"] = parts[0]
        codes["scene"] = parts[1]
    return codes