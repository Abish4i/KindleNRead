# Minimal RSS to Kindle Example
# This is a simplified version showing the core workflow

import feedparser
from newspaper import Article
from ebooklib import epub
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta
import os

# Configuration
CONFIG = {
    'feeds': [
        {'name': 'Tech News', 'url': 'https://techcrunch.com/feed/'},
        {'name': 'Python Weekly', 'url': 'https://www.pythonweekly.com/rss/'}
    ],
    'kindle_email': 'yourname@kindle.com',
    'smtp': {
        'host': 'smtp.gmail.com',
        'port': 587,
        'username': 'your-email@gmail.com',
        'password': 'your-app-password'
    },
    'max_articles_per_feed': 5,
    'days_old': 1
}

def fetch_articles(feeds, max_articles, days_old):
    """Fetch articles from RSS feeds"""
    articles = []
    cutoff_date = datetime.now() - timedelta(days=days_old)
    
    for feed in feeds:
        print(f"Fetching {feed['name']}...")
        parsed = feedparser.parse(feed['url'])
        
        for entry in parsed.entries[:max_articles]:
            try:
                # Get publication date
                pub_date = datetime(*entry.published_parsed[:6])
                
                if pub_date >= cutoff_date:
                    articles.append({
                        'title': entry.title,
                        'url': entry.link,
                        'feed_name': feed['name'],
                        'date': pub_date
                    })
            except Exception as e:
                print(f"Error parsing entry: {e}")
                
    return articles

def extract_content(article_data):
    """Extract full article content using newspaper3k"""
    try:
        article = Article(article_data['url'])
        article.download()
        article.parse()
        
        article_data['content'] = article.text
        article_data['authors'] = article.authors
        return article_data
    except Exception as e:
        print(f"Error extracting {article_data['title']}: {e}")
        return None

def create_epub(articles, output_file):
    """Generate EPUB from articles"""
    book = epub.EpubBook()
    
    # Set metadata
    book.set_identifier(f'rss_digest_{datetime.now().strftime("%Y%m%d")}')
    book.set_title(f'Daily Digest - {datetime.now().strftime("%Y-%m-%d")}')
    book.set_language('en')
    book.add_author('RSS Aggregator')
    
    # Create chapters
    chapters = []
    for idx, article in enumerate(articles):
        if article and article.get('content'):
            chapter = epub.EpubHtml(
                title=article['title'],
                file_name=f'article_{idx}.xhtml',
                lang='en'
            )
            
            content_html = f"""
                <h1>{article['title']}</h1>
                <p><em>Source: {article['feed_name']}</em></p>
                <p><em>Date: {article['date'].strftime("%Y-%m-%d %H:%M")}</em></p>
                <hr/>
                <div>{article['content'].replace(chr(10), '</p><p>')}</div>
            """
            chapter.content = content_html
            
            book.add_item(chapter)
            chapters.append(chapter)
    
    # Add navigation
    book.toc = tuple(chapters)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    
    # Define spine
    book.spine = ['nav'] + chapters
    
    # Write EPUB
    epub.write_epub(output_file, book)
    print(f"EPUB created: {output_file}")

def send_to_kindle(epub_file, config):
    """Send EPUB to Kindle via email"""
    msg = MIMEMultipart()
    msg['From'] = config['smtp']['username']
    msg['To'] = config['kindle_email']
    msg['Subject'] = f'Daily Digest - {datetime.now().strftime("%Y-%m-%d")}'
    
    # Attach EPUB file
    with open(epub_file, 'rb') as f:
        part = MIMEBase('application', 'epub+zip')
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename={os.path.basename(epub_file)}'
        )
        msg.attach(part)
    
    # Send email
    try:
        server = smtplib.SMTP(config['smtp']['host'], config['smtp']['port'])
        server.starttls()
        server.login(config['smtp']['username'], config['smtp']['password'])
        server.send_message(msg)
        server.quit()
        print(f"Email sent to {config['kindle_email']}")
    except Exception as e:
        print(f"Error sending email: {e}")

def main():
    """Main execution pipeline"""
    print("=== RSS to Kindle Pipeline ===\n")
    
    # 1. Fetch articles from RSS feeds
    print("Step 1: Fetching RSS feeds...")
    articles = fetch_articles(
        CONFIG['feeds'],
        CONFIG['max_articles_per_feed'],
        CONFIG['days_old']
    )
    print(f"Found {len(articles)} articles\n")
    
    # 2. Extract full content
    print("Step 2: Extracting full article content...")
    for article in articles:
        extract_content(article)
    extracted = len([a for a in articles if a.get('content')])
    print(f"Extracted content for {extracted} articles\n")
    
    # 3. Generate EPUB
    print("Step 3: Generating EPUB...")
    output_file = f'digest_{datetime.now().strftime("%Y%m%d")}.epub'
    create_epub(articles, output_file)
    
    # 4. Send to Kindle
    print("\nStep 4: Sending to Kindle...")
    send_to_kindle(output_file, CONFIG)
    
    # 5. Cleanup
    print("\nStep 5: Cleaning up...")
    # os.remove(output_file)  # Uncomment to delete after sending
    
    print("\n=== Pipeline Complete ===")

if __name__ == '__main__':
    main()


# USAGE INSTRUCTIONS:
# 
# 1. Install required libraries:
#    pip install feedparser newspaper3k ebooklib lxml pillow
#
# 2. Update CONFIG dictionary with your settings:
#    - kindle_email: Your Kindle email (find in Amazon account)
#    - smtp settings: Use Gmail app password (not regular password)
#
# 3. Optional: Add Calibre for MOBI conversion
#    - Install Calibre desktop application
#    - Run: ebook-convert digest.epub digest.mobi
#
# 4. Run the script:
#    python rss_kindle_minimal.py
