#!/usr/bin/env python3
"""
RSS to PDF Kindle Emailer
Converts RSS feed articles to PDF and sends them to Kindle email.
"""

import argparse
import logging
import os
import sys
import socket
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

import feedparser
import urllib.request
import urllib.error
from bs4 import BeautifulSoup


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class RSSFeedProcessor:
    """Handles RSS feed parsing and article extraction."""
    
    def __init__(self, timeout: int = 30):
        """Initialize with configurable timeout and retry settings."""
        self.timeout = timeout
    
    def parse_feed(self, feed_url: str) -> List[Dict[str, str]]:
        """
        Parse RSS feed and return list of articles.
        
        Args:
            feed_url: URL of the RSS feed
            
        Returns:
            List of dictionaries containing article title, link, and published date
        """
        try:
            logger.info(f"Parsing RSS feed: {feed_url}")
            feed = feedparser.parse(feed_url)
            
            if feed.bozo:
                logger.warning(f"Feed parsing warning: {feed.bozo_exception}")
            
            if not feed.entries:
                logger.error("No entries found in the feed")
                return []
            
            articles = []
            for entry in feed.entries:
                articles.append({
                    'title': entry.get('title', 'Untitled'),
                    'link': entry.get('link', ''),
                    'published': entry.get('published', 'No date'),
                    'summary': entry.get('summary', '')
                })
            
            logger.info(f"Found {len(articles)} articles in feed")
            return articles
            
        except Exception as e:
            logger.error(f"Error parsing RSS feed: {e}")
            return []
    
    def extract_article_content(self, article_url: str) -> str:
        """
        Extract article content from URL with improved selectors.
        
        Args:
            article_url: URL of the article
            
        Returns:
            Extracted article content as string
        """
        try:
            logger.debug(f"Extracting content from: {article_url}")
            with urllib.request.urlopen(article_url, timeout=self.timeout) as response:
                content = response.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup.find_all(['script', 'style', 'nav', 'footer', 'aside']):
                element.decompose()
            
            # Try multiple selectors in order of specificity
            selectors = [
                ('div', 'post-body'),
                ('article', None),
                ('div', 'entry-content'),
                ('div', 'content'),
                ('div', 'post-content'),
                ('div', 'article-content'),
                ('main', None),
            ]
            
            content = None
            for tag, class_name in selectors:
                if class_name:
                    content = soup.find(tag, class_=class_name)
                else:
                    content = soup.find(tag)
                
                if content:
                    # Remove labels/tags sections
                    for div in content.find_all("div", {'class': ['post-labels', 'tags', 'categories']}):
                        div.decompose()
                    break
            
            if content:
                return content.get_text(separator='\n', strip=True)
            else:
                logger.warning(f"Could not extract article content from {article_url}")
                return "Content extraction failed. Please visit the original article."
                
        except socket.timeout:
            logger.error(f"Timeout while fetching article: {article_url}")
            return "Error: Request timed out"
        except urllib.error.URLError as e:
            logger.error(f"Error fetching article {article_url}: {e.reason}")
            return f"Error fetching article: {e.reason}"
        except Exception as e:
            logger.error(f"Unexpected error extracting content: {e}")
            return "Unexpected error occurred"


class TextFileGenerator:
    """Handles text file generation from article content."""
    
    @staticmethod
    def generate_text_content(articles: List[Dict[str, str]], feed_title: str = "RSS Feed") -> str:
        """
        Generate a single text string from articles.
        
        Args:
            articles: List of article dictionaries
            feed_title: Title for the document
            
        Returns:
            Text string
        """
        text_content = f"# {feed_title}\n"
        text_content += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        text_content += "## Table of Contents\n"
        for i, article in enumerate(articles, 1):
            text_content += f"{i}. {article['title']}\n"
        text_content += "\n" + "="*80 + "\n\n"
        
        for article in articles:
            text_content += f"## {article['title']}\n"
            text_content += f"Published: {article.get('published', 'Unknown')}\n\n"
            text_content += f"{article['content']}\n\n"
            text_content += "="*80 + "\n\n"

        return text_content
    
    @staticmethod
    def save_as_txt(text_content: str, output_path: Path) -> bool:
        """
        Save text content to a file.
        
        Args:
            text_content: Text string to save
            output_path: Path for output text file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text_content)
            logger.info(f"Successfully created text file: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error creating text file: {e}")
            return False


class EmailSender:
    """Handles email operations for sending PDFs to Kindle."""
    
    def __init__(self, sender_email: str, sender_password: str):
        """Initialize email sender with credentials."""
        self.sender_email = sender_email
        self.sender_password = sender_password
    
    def send_email(
        self,
        recipient_email: str,
        subject: str,
        body: str,
        attachment_path: Path
    ) -> bool:
        """
        Send email with text file attachment.
        
        Args:
            recipient_email: Recipient's email address
            subject: Email subject
            body: Email body text
            attachment_path: Path to text file attachment
            
        Returns:
            True if successful, False otherwise
        """
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach TXT
            with open(attachment_path, "r", encoding="utf-8") as f:
                part = MIMEApplication(f.read(), Name=attachment_path.name)
            
            part['Content-Disposition'] = f'attachment; filename="{attachment_path.name}"'
            msg.attach(part)
            
            # Send email
            logger.info("Connecting to Gmail SMTP server...")
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.sendmail(self.sender_email, recipient_email, msg.as_string())
            server.quit()
            
            logger.info(f"Email sent successfully to {recipient_email}")
            return True
            
        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP authentication failed. Use Gmail App Password if 2FA is enabled.")
            logger.error("Generate one at: https://myaccount.google.com/apppasswords")
            return False
        except (socket.gaierror, smtplib.SMTPConnectError) as e:
            logger.error(f"Could not connect to SMTP server: {e}")
            return False
        except FileNotFoundError:
            logger.error(f"Attachment file not found: {attachment_path}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending email: {e}")
            return False


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Convert RSS feed to PDF and email to Kindle",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example RSS feeds:
  - BBC News: http://feeds.bbci.co.uk/news/rss.xml
  - TechCrunch: https://techcrunch.com/feed/
  - The Hindu: https://www.thehindu.com/news/national/feeder/default.rss
  - Python Blog: https://blog.python.org/feeds/posts/default.rss
  
Environment variables:
  SENDER_EMAIL: Your Gmail address
  SENDER_PASSWORD: Your Gmail app password (not regular password)
  
Note: For Gmail, you need to use an App Password if 2FA is enabled.
Generate one at: https://myaccount.google.com/apppasswords
        """
    )
    
    parser.add_argument(
        "rss_url",
        help="URL of the RSS feed to process"
    )
    parser.add_argument(
        "kindle_email",
        help="Your Kindle email address (e.g., username@kindle.com)"
    )
    parser.add_argument(
        "--sender_email",
        help="Gmail address for sending (or set SENDER_EMAIL env var)",
        default=os.environ.get("SENDER_EMAIL")
    )
    parser.add_argument(
        "--sender_password",
        help="Gmail app password (or set SENDER_PASSWORD env var)",
        default=os.environ.get("SENDER_PASSWORD")
    )
    parser.add_argument(
        "--output_filename",
        help="Output text filename",
        default=f"rss_feed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    )
    parser.add_argument(
        "--max_articles",
        help="Maximum number of articles to process",
        type=int,
        default=10
    )
    parser.add_argument(
        "--dry_run",
        help="Generate text file but don't send email",
        action="store_true"
    )
    parser.add_argument(
        "--verbose",
        help="Enable verbose logging",
        action="store_true"
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Validate inputs
    if not args.dry_run and not (args.sender_email and args.sender_password):
        logger.error("Sender credentials required. Use --sender_email and --sender_password or set environment variables.")
        sys.exit(1)
    
    # Process RSS feed
    processor = RSSFeedProcessor()
    articles = processor.parse_feed(args.rss_url)
    
    if not articles:
        logger.error("No articles found. Exiting.")
        sys.exit(1)
    
    # Extract article content
    articles_with_content = []
    for i, article in enumerate(articles[:args.max_articles], 1):
        logger.info(f"[{i}/{min(args.max_articles, len(articles))}] Processing: {article['title']}")
        content = processor.extract_article_content(article['link'])
        articles_with_content.append({
            'title': article['title'],
            'content': content,
            'published': article.get('published', 'Unknown'),
            'link': article['link']
        })
    
    # Generate text file
    text_generator = TextFileGenerator()
    text_content = text_generator.generate_text_content(articles_with_content, "RSS Feed Digest")
    output_path = Path(args.output_filename)
    
    if not text_generator.save_as_txt(text_content, output_path):
        logger.error("Text file generation failed. Exiting.")
        sys.exit(1)
    
    # Send email or dry run
    if args.dry_run:
        logger.info("\n" + "="*50)
        logger.info("DRY RUN MODE - No email sent")
        logger.info("="*50)
        logger.info(f"To: {args.kindle_email}")
        logger.info(f"From: {args.sender_email}")
        logger.info(f"Subject: RSS Feed Digest")
        logger.info(f"Attachment: {output_path}")
        logger.info(f"File size: {output_path.stat().st_size / 1024:.2f} KB")
        logger.info("="*50)
    else:
        email_sender = EmailSender(args.sender_email, args.sender_password)
        success = email_sender.send_email(
            args.kindle_email,
            "RSS Feed Digest",
            f"Attached is your RSS feed digest with {len(articles_with_content)} articles.",
            output_path
        )
        
        if not success:
            logger.error("Email sending failed.")
            sys.exit(1)
    
    logger.info("Process completed successfully!")


if __name__ == "__main__":
    main()
