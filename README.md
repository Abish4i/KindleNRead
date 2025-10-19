# KindleNRead
## Dependencies

* Python 3
* `feedparser`
* `requests`
* `beautifulsoup4`
* `pdfkit`
* `wkhtmltopdf`

To install the Python libraries, run:
## Usage

```bash
python3 rss_to_kindle.py <rss_url> <kindle_email> [options]
```

* `rss_url`: The URL of the RSS feed.
* `kindle_email`: Your Kindle email address.

### Options

* `--sender_email`: Your email address for sending the file.
* `--sender_password`: Your email password.
* `--output_filename`: The name of the output PDF file (default: `rss_feed.pdf`).
* `--max_articles`: The maximum number of articles to process (default: 10).

You can also set the `SENDER_EMAIL` and `SENDER_PASSWORD` environment variables instead of using the command-line arguments.
