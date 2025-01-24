def extract_image_path(message: str) -> str:
    import re
    match = re.search(r"!\[.*?\]\((.*?)\)", message)
    return match.group(1) if match else None
