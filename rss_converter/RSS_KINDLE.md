# GitHub Copilot Prompt: RSS Feed to Kindle Delivery System

## Project Overview
Create a Python-based RSS to Kindle delivery system similar to Calibre's "Fetch News" feature. The system should automatically fetch articles from RSS feeds, compile them into an ebook format (EPUB/MOBI), and send them to a Kindle device via email.

## Core Requirements

### 1. RSS Feed Management
- Parse multiple RSS/ATOM feeds from a configuration file
- Support custom feed sources (tech news, blogs, magazines)
- Filter articles by date (e.g., last 24 hours, last 7 days)
- Filter articles by keywords (include/exclude patterns)
- Handle feed metadata (title, author, publication date)

### 2. Content Extraction
- Download full article content from URLs (not just RSS summaries)
- Extract clean text content without ads and navigation
- Preserve article images and embed them in the ebook
- Handle various article formats and website structures
- Use intelligent parsing to extract main content
- Support for custom extraction rules per domain

### 3. Ebook Generation
- Create EPUB format with proper structure:
  - Cover page with publication date
  - Table of contents with sections per feed
  - Individual chapters for each article
  - Proper metadata (title, author, date, description)
- Support images with optimization for e-readers
- Generate readable formatting (proper spacing, headers, paragraphs)
- Optional: Convert EPUB to MOBI using Calibre's ebook-convert

### 4. Email Delivery
- Send generated ebook to Kindle email address
- Support SMTP authentication (Gmail, Outlook, custom)
- Handle file attachments (EPUB or MOBI)
- Include descriptive email subject and body
- Error handling for email delivery failures

### 5. Scheduling & Automation
- Daily automated runs at specified time
- Weekly digest option
- Support for cron-like scheduling
- Logging of successful and failed operations
- Retry mechanism for failed feed fetches

### 6. Configuration Management
- YAML or JSON configuration file for:
  - List of RSS feeds with names and URLs
  - Kindle email address
  - SMTP server settings (host, port, username, password)
  - Schedule settings (time, frequency)
  - Article filters (date range, keywords, max articles per feed)
  - Output preferences (format, title template)

## Technical Stack

### Required Libraries
```python
# Install these packages
feedparser           # RSS/ATOM feed parsing
newspaper3k          # Article extraction (or newspaper4k for updated version)
ebooklib            # EPUB creation
beautifulsoup4      # HTML parsing
lxml                # XML/HTML processing
requests            # HTTP requests
python-dateutil     # Date handling
schedule            # Task scheduling
pyyaml              # Configuration file parsing
pillow              # Image processing
```

### Optional Tools
- Calibre CLI (`ebook-convert`) for MOBI conversion
- `readability-lxml` for alternative article extraction
- `nltk` for text processing and summarization

## Architecture & Components

### Component 1: Configuration Manager
```python
class ConfigManager:
    """
    Load and validate configuration from config.yaml
    - RSS feeds list
    - Kindle email settings
    - SMTP credentials
    - Scheduling preferences
    - Filter settings
    """
```

### Component 2: Feed Fetcher
```python
class FeedFetcher:
    """
    Fetch RSS feeds and parse entries
    - Use feedparser to parse RSS/ATOM feeds
    - Extract entry metadata (title, link, date, summary)
    - Filter entries by date and keywords
    - Return list of article URLs to process
    """
```

### Component 3: Article Extractor
```python
class ArticleExtractor:
    """
    Extract full article content from URLs
    - Use newspaper3k for intelligent content extraction
    - Download article and parse HTML
    - Extract: title, authors, text, images, date
    - Clean up content (remove ads, nav elements)
    - Handle extraction failures gracefully
    """
```

### Component 4: EPUB Generator
```python
class EpubGenerator:
    """
    Create EPUB ebook from articles
    - Initialize epub.EpubBook() from ebooklib
    - Set metadata (title, author, date, identifier)
    - Create cover page with publication info
    - Add each article as a chapter (EpubHtml)
    - Generate table of contents (TOC)
    - Embed images (EpubImage)
    - Define spine and add navigation
    - Write EPUB file to disk
    """
```

### Component 5: Format Converter
```python
class FormatConverter:
    """
    Convert EPUB to MOBI using Calibre
    - Check if ebook-convert is installed
    - Run subprocess: ebook-convert input.epub output.mobi
    - Optional: add conversion parameters for Kindle optimization
    - Handle conversion errors
    """
```

### Component 6: Email Sender
```python
class EmailSender:
    """
    Send ebook to Kindle via email
    - Connect to SMTP server (Gmail, Outlook, etc.)
    - Create email with attachment
    - Set proper MIME types for EPUB/MOBI
    - Send to Kindle email address
    - Handle authentication and SSL/TLS
    - Log success/failure
    """
```

### Component 7: Scheduler
```python
class Scheduler:
    """
    Automate daily/weekly runs
    - Use schedule library for task scheduling
    - Run main pipeline at specified time
    - Handle exceptions and retries
    - Log each run
    """
```

## Implementation Workflow

### Main Pipeline
```python
def main_pipeline():
    """
    1. Load configuration from config.yaml
    2. Initialize all components
    3. Fetch RSS feeds and get article list
    4. Extract full content from each article
    5. Generate EPUB with all articles
    6. Convert to MOBI (optional)
    7. Send to Kindle via email
    8. Clean up temporary files
    9. Log completion status
    """
```

## Configuration File Example (config.yaml)

```yaml
feeds:
  - name: "Tech News"
    url: "https://techcrunch.com/feed/"
  - name: "Python Weekly"
    url: "https://www.pythonweekly.com/rss/"
  - name: "Hacker News"
    url: "https://hnrss.org/frontpage"

kindle:
  email: "yourname@kindle.com"

smtp:
  host: "smtp.gmail.com"
  port: 587
  username: "your-email@gmail.com"
  password: "your-app-password"
  use_tls: true

filters:
  max_articles_per_feed: 10
  oldest_article_days: 1
  keywords_include: []
  keywords_exclude: ["advertisement", "sponsored"]

ebook:
  title_template: "Daily Digest - {date}"
  format: "epub"  # or "mobi"
  include_images: true
  cover_template: "My Daily News"

schedule:
  frequency: "daily"
  time: "06:00"
```

## Error Handling & Logging

```python
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rss_kindle.log'),
        logging.StreamHandler()
    ]
)

# Use throughout application
logger = logging.getLogger(__name__)
logger.info("Starting RSS fetch...")
logger.error("Failed to fetch feed: {error}")
```

## Code Structure Example

```
rss-to-kindle/
├── config.yaml              # Configuration file
├── main.py                  # Entry point
├── requirements.txt         # Python dependencies
├── src/
│   ├── __init__.py
│   ├── config_manager.py    # Config loading
│   ├── feed_fetcher.py      # RSS fetching
│   ├── article_extractor.py # Content extraction
│   ├── epub_generator.py    # EPUB creation
│   ├── format_converter.py  # EPUB to MOBI
│   ├── email_sender.py      # Email delivery
│   └── scheduler.py         # Automation
├── templates/
│   └── cover_template.html  # Cover page template
└── output/                  # Generated ebooks
```

## Key Implementation Notes

### Article Extraction Best Practices
```python
from newspaper import Article

article = Article(url)
article.download()
article.parse()

# Extract data
title = article.title
text = article.text
authors = article.authors
publish_date = article.publish_date
top_image = article.top_image
```

### EPUB Generation Best Practices
```python
from ebooklib import epub

book = epub.EpubBook()
book.set_identifier('rss_digest_001')
book.set_title('Daily News Digest')
book.set_language('en')

# Add chapter
chapter = epub.EpubHtml(title='Article Title', file_name='article1.xhtml')
chapter.content = '<h1>Article Title</h1><p>Content...</p>'
book.add_item(chapter)

# Generate TOC and spine
book.toc = (epub.Link('article1.xhtml', 'Article Title', 'article1'),)
book.spine = ['nav', chapter]

# Write EPUB
epub.write_epub('output.epub', book)
```

### Email Sending Best Practices
```python
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

msg = MIMEMultipart()
msg['From'] = sender_email
msg['To'] = kindle_email
msg['Subject'] = 'Daily News Digest'

# Attach EPUB
with open('output.epub', 'rb') as f:
    part = MIMEBase('application', 'epub+zip')
    part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment', filename='digest.epub')
    msg.attach(part)

# Send
server = smtplib.SMTP(smtp_host, smtp_port)
server.starttls()
server.login(username, password)
server.send_message(msg)
server.quit()
```

## Advanced Features (Optional)

1. **Content Summarization**: Use NLP to generate article summaries
2. **Article Deduplication**: Skip duplicate articles across feeds
3. **Custom CSS Styling**: Apply custom styles to EPUB
4. **Web Interface**: Flask/FastAPI dashboard for management
5. **Multiple Kindle Support**: Send to multiple devices
6. **Pocket/Instapaper Integration**: Include saved articles
7. **Article Translation**: Auto-translate non-English articles
8. **Text-to-Speech**: Generate audiobook MP3 files

## Testing Checklist

- [ ] Successfully parse multiple RSS feeds
- [ ] Extract full article content with images
- [ ] Generate valid EPUB file (test in Calibre)
- [ ] Convert EPUB to MOBI successfully
- [ ] Send email with attachment to Kindle
- [ ] Verify articles appear on Kindle device
- [ ] Test scheduling and automation
- [ ] Handle feed fetch failures gracefully
- [ ] Test with various article formats
- [ ] Verify proper cleanup of temporary files

## Security Considerations

1. Store SMTP passwords securely (use environment variables or keyring)
2. Never commit credentials to version control
3. Use app-specific passwords for email (not main password)
4. Validate RSS feed URLs before fetching
5. Sanitize HTML content before generating ebooks
6. Set reasonable rate limits for article fetching

## Performance Optimizations

1. Implement concurrent article fetching (threading/asyncio)
2. Cache downloaded articles to avoid re-fetching
3. Compress images for smaller ebook size
4. Set reasonable limits on articles per feed
5. Implement exponential backoff for failed requests

## Deployment Options

1. **Local Machine**: Run as background service/daemon
2. **Raspberry Pi**: Lightweight 24/7 server
3. **Cloud VPS**: Linode, DigitalOcean, AWS EC2
4. **Docker Container**: Portable containerized deployment
5. **GitHub Actions**: Free automated runs (with caveats)

---

## Example GitHub Copilot Prompts

### Prompt 1: Feed Fetcher
```
Create a Python class FeedFetcher that uses feedparser to fetch multiple RSS feeds from a list of URLs. 
The class should:
1. Accept a list of feed URLs and names
2. Parse each feed and extract entries
3. Filter entries by date (only last N days)
4. Filter by keywords (include/exclude)
5. Return a list of dictionaries with article metadata (title, url, date, summary)
6. Handle errors gracefully for failed feeds
7. Log all operations
```

### Prompt 2: Article Extractor
```
Create a Python class ArticleExtractor that uses newspaper3k to extract full article content from URLs.
The class should:
1. Download article from URL
2. Parse and extract: title, authors, text, publish_date, top_image
3. Clean text content (remove extra whitespace)
4. Download and include article images
5. Handle extraction failures with fallback to BeautifulSoup
6. Return structured article data as dictionary
7. Implement retry logic for failed downloads
```

### Prompt 3: EPUB Generator
```
Create a Python class EpubGenerator that uses ebooklib to create EPUB ebooks from article data.
The class should:
1. Initialize epub.EpubBook with metadata
2. Add a cover page with publication title and date
3. Create chapters from article list (one chapter per article)
4. Embed article images as EpubImage items
5. Generate table of contents grouped by feed source
6. Set proper spine and navigation
7. Write EPUB file to specified path
8. Support custom CSS styling
```

### Prompt 4: Email Sender
```
Create a Python class EmailSender for sending ebooks to Kindle via email.
The class should:
1. Connect to SMTP server (support Gmail, Outlook, custom)
2. Create email with proper MIME structure
3. Attach EPUB or MOBI file
4. Set appropriate headers and subject
5. Handle SSL/TLS authentication
6. Implement retry logic for failed sends
7. Log success/failure with details
8. Support both app passwords and OAuth
```

### Prompt 5: Main Pipeline
```
Create the main pipeline function that orchestrates the RSS to Kindle workflow:
1. Load configuration from YAML file
2. Initialize all components (FeedFetcher, ArticleExtractor, EpubGenerator, EmailSender)
3. Fetch RSS feeds and get article list
4. Extract full content for each article (with progress tracking)
5. Generate EPUB with all articles
6. Optionally convert EPUB to MOBI using Calibre CLI
7. Send to Kindle email address
8. Clean up temporary files
9. Log complete workflow with timing
10. Handle exceptions at each step
```

---

## Complete Project Prompt for GitHub Copilot

```
Create a complete Python application that automatically fetches RSS feeds, extracts full article content, 
compiles them into an EPUB ebook, and sends it to a Kindle device via email (similar to Calibre's Fetch News feature).

Requirements:
- Modular architecture with separate classes for feed fetching, content extraction, ebook generation, and email sending
- Configuration via YAML file (feeds, Kindle email, SMTP settings, filters)
- Support multiple RSS feeds with customizable names
- Extract full article content (not just RSS summaries) using newspaper3k
- Generate EPUB format with table of contents, cover page, and embedded images
- Send to Kindle email address via SMTP
- Schedule daily/weekly automated runs
- Comprehensive error handling and logging
- Filter articles by date and keywords

Technical stack:
- feedparser for RSS parsing
- newspaper3k for article extraction
- ebooklib for EPUB generation
- smtplib for email delivery
- schedule for automation
- pyyaml for configuration

Project structure:
- config.yaml for settings
- src/ directory with modular components
- main.py as entry point
- requirements.txt for dependencies
- Proper logging and error handling throughout

Additional features:
- Convert EPUB to MOBI using Calibre CLI (optional)
- Support for custom article filters
- Progress tracking during execution
- Cleanup of temporary files after completion
```
