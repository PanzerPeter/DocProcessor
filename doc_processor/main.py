import argparse
import json
import sys

from extractor import extract
from categorizer import categorize
from utils import validate_file


def process(filepath: str) -> dict:
    validate_file(filepath)
    raw = extract(filepath)
    if not raw.strip():
        raise ValueError("No text extracted from document.")
    result = categorize(raw)
    result["source_file"] = filepath
    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract and categorize documents (PDF/images) using AI.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py invoice.pdf
  python main.py scan.png
  python main.py contract.pdf --output result.json
        """,
    )
    parser.add_argument("file", help="Path to PDF or image file to process")
    parser.add_argument(
        "--output", "-o", help="Write JSON output to file instead of stdout"
    )
    parser.add_argument(
        "--pretty", action="store_true", default=True, help="Pretty-print JSON output (default: true)"
    )
    args = parser.parse_args()

    try:
        result = process(args.file)
        indent = 2 if args.pretty else None
        output_json = json.dumps(result, ensure_ascii=False, indent=indent)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output_json)
            print(f"Output written to {args.output}", file=sys.stderr)
        else:
            print(output_json)

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
