"""Requirements-document invocation shim: ``python gmail_pdf_downloader.py --help``."""

from gmail_pdf.cli.main import main

if __name__ == "__main__":
    raise SystemExit(main())
