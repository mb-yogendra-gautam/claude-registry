"""Extract text from a PDF. Placeholder — replace with real implementation."""
import sys

def extract(path: str) -> str:
    # In a real skill, use pypdf or pdfplumber here.
    return f"[stub] would extract text from {path}"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: extract.py <pdf-path>", file=sys.stderr)
        sys.exit(1)
    print(extract(sys.argv[1]))
