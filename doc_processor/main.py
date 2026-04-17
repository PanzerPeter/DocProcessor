from __future__ import annotations

import argparse
import csv
import io
import json
import logging
import sys
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table

from categorizer import categorize
from config import CFG
from exceptions import DocProcessorError, EmptyDocumentError
from extractor import extract
from models import DocumentResult
from utils import collect_files, validate_file

console = Console()
err_console = Console(stderr=True)


# ---------------------------------------------------------------------------
# Core pipeline
# ---------------------------------------------------------------------------

def process_file(filepath: str) -> DocumentResult:
    validate_file(filepath)
    extraction = extract(filepath)

    if not extraction.text.strip():
        raise EmptyDocumentError(f"No text extracted from '{Path(filepath).name}'.")

    result = categorize(extraction.text, source_file=filepath)
    result.page_count = extraction.page_count
    result.char_count = extraction.char_count
    return result


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------

def _to_json(results: list[DocumentResult], indent: int) -> str:
    data = [r.to_dict() for r in results]
    payload = data[0] if len(data) == 1 else data
    return json.dumps(payload, ensure_ascii=False, indent=indent)


def _to_jsonl(results: list[DocumentResult]) -> str:
    lines = [json.dumps(r.to_dict(), ensure_ascii=False) for r in results]
    return "\n".join(lines)


def _to_csv(results: list[DocumentResult]) -> str:
    if not results:
        return ""
    buf = io.StringIO()
    fields = ["source_file", "category", "language", "confidence", "summary", "page_count", "char_count"]
    writer = csv.DictWriter(buf, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    for r in results:
        writer.writerow(r.to_dict())
    return buf.getvalue()


def _print_summary_table(results: list[DocumentResult], errors: list[tuple[str, str]]) -> None:
    table = Table(title="Processing Summary", show_lines=True)
    table.add_column("File", style="cyan", no_wrap=True)
    table.add_column("Category", style="green")
    table.add_column("Language")
    table.add_column("Confidence", justify="right")
    table.add_column("Pages", justify="right")
    table.add_column("Status")

    for r in results:
        conf_color = "green" if r.confidence >= 0.8 else "yellow" if r.confidence >= 0.5 else "red"
        table.add_row(
            Path(r.source_file).name,
            r.category.value,
            r.language,
            f"[{conf_color}]{r.confidence:.0%}[/{conf_color}]",
            str(r.page_count or "-"),
            "[green]OK[/green]",
        )
    for filepath, error in errors:
        table.add_row(
            Path(filepath).name, "-", "-", "-", "-",
            f"[red]FAILED[/red]",
        )

    err_console.print(table)
    if errors:
        err_console.print("[bold red]Errors:[/bold red]")
        for filepath, error in errors:
            err_console.print(f"  [red]{Path(filepath).name}[/red]: {error}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="doc-processor",
        description="Extract and categorize documents (PDF/images) using AI.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  doc-processor invoice.pdf
  doc-processor *.pdf --format jsonl --output results.jsonl
  doc-processor scans/ --output-dir results/ --min-confidence 0.8
  doc-processor report.pdf --verbose
        """,
    )
    parser.add_argument(
        "files",
        nargs="+",
        help="PDF/image files or directories to process",
    )
    parser.add_argument(
        "--output", "-o",
        help="Write output to file (default: stdout)",
    )
    parser.add_argument(
        "--output-dir",
        help="Write one JSON file per input into this directory",
        metavar="DIR",
    )
    parser.add_argument(
        "--format", "-f",
        choices=["json", "jsonl", "csv"],
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--min-confidence",
        type=float,
        default=CFG.min_confidence,
        metavar="FLOAT",
        help="Skip results below this confidence threshold (default: 0.0)",
    )
    parser.add_argument(
        "--no-summary",
        action="store_true",
        help="Suppress the results table printed to stderr",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable debug logging",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else getattr(logging, CFG.log_level, logging.WARNING)
    logging.basicConfig(
        level=log_level,
        handlers=[RichHandler(console=err_console, show_path=False, rich_tracebacks=True)],
        format="%(message)s",
    )

    # Resolve all input paths
    filepaths = collect_files(args.files)
    if not filepaths:
        err_console.print("[red]No supported files found.[/red]")
        sys.exit(1)

    results: list[DocumentResult] = []
    errors: list[tuple[str, str]] = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        TimeElapsedColumn(),
        console=err_console,
        transient=True,
    ) as progress:
        task = progress.add_task("Processing documents...", total=len(filepaths))
        for fp in filepaths:
            progress.update(task, description=f"[cyan]{Path(fp).name}[/cyan]")
            try:
                result = process_file(fp)
                if result.confidence >= args.min_confidence:
                    results.append(result)
                else:
                    logging.warning(
                        "Skipping '%s': confidence %.2f < %.2f",
                        Path(fp).name, result.confidence, args.min_confidence,
                    )
            except DocProcessorError as e:
                errors.append((fp, str(e)))
                logging.error("%s", e)
            progress.advance(task)

    # Per-file output directory mode
    if args.output_dir:
        out_dir = Path(args.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        for r in results:
            stem = Path(r.source_file).stem
            out_path = out_dir / f"{stem}.json"
            out_path.write_text(
                json.dumps(r.to_dict(), ensure_ascii=False, indent=CFG.output_indent),
                encoding="utf-8",
            )
        if not args.no_summary:
            _print_summary_table(results, errors)
        err_console.print(f"[green]Wrote {len(results)} file(s) to {out_dir}/[/green]")
    else:
        # Single output / stdout
        if args.format == "json":
            output_text = _to_json(results, CFG.output_indent)
        elif args.format == "jsonl":
            output_text = _to_jsonl(results)
        else:
            output_text = _to_csv(results)

        if args.output:
            Path(args.output).write_text(output_text, encoding="utf-8")
            if not args.no_summary:
                _print_summary_table(results, errors)
            err_console.print(f"[green]Output written to {args.output}[/green]")
        else:
            if not args.no_summary and len(filepaths) > 1:
                _print_summary_table(results, errors)
            print(output_text)

    if errors:
        sys.exit(1 if results else 2)


if __name__ == "__main__":
    main()
