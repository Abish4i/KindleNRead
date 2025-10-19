import feedparser
import requests
from bs4 import BeautifulSoup
import pdfkit
import smtplib
import argparse
import os
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(sender_email, sender_password, recipient_email, subject, body, attachment_path):
    """
    Sends an email with an attachment.

    Args:
        sender_email: The email address of the sender.
        sender_password: The password of the sender.
        recipient_email: The email address of the recipient.
        subject: The subject of the email.
        body: The body of the email.
        attachment_path: The path to the file to attach.
    """
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    with open(attachment_path, "rb") as f:
        part = MIMEApplication(
            f.read(),
            Name=os.path.basename(attachment_path)
        )
    part['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment_path)}"'
    msg.attach(part)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, recipient_email, text)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

def extract_article_content(article_url):
    """
    Extracts the content of an article from its URL.

    Args:
        article_url: The URL of the article.

    Returns:
        The content of the article as a string.
    """
    try:
        response = requests.get(article_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        # This is a more specific selector for Blogspot.
        article_body = soup.find('div', class_='post-body')
        if article_body:
            # Get rid of the "Labels" section
            for div in article_body.find_all("div", {'class':'post-labels'}):
                div.decompose()
            return article_body.get_text(separator='\\n', strip=True)
        else:
            # Fallback to the generic one if the specific one fails
            article_body = soup.find('article') or soup.find('div', class_='content') or soup.find('div', class_='post')
            if article_body:
                return article_body.get_text(separator='\\n', strip=True)
            else:
                return "Could not extract article content."
    except requests.exceptions.RequestException as e:
        return f"Error fetching article: {e}"

def parse_rss_feed(feed_url):
    """
    Parses an RSS feed and returns a list of articles.

    Args:
        feed_url: The URL of the RSS feed.

    Returns:
        A list of dictionaries, where each dictionary represents an article
        and contains the title and link.
    """
    feed = feedparser.parse(feed_url)
    articles = []
    for entry in feed.entries:
        articles.append({
            'title': entry.title,
            'link': entry.link
        })
    return articles

def convert_to_pdf(articles, output_filename):
    """
    Converts a list of articles to a PDF file.

    Args:
        articles: A list of dictionaries, where each dictionary represents an
                  article and contains the title and content.
        output_filename: The name of the output PDF file.
    """
    html = "<html><head><meta charset='utf-8'></head><body>"
    for article in articles:
        html += f"<h1>{article['title']}</h1>"
        html += f"<div>{article['content']}</div>"
        html += "<hr>"
    html += "</body></html>"

    try:
        pdfkit.from_string(html, output_filename)
        print(f"Successfully created {output_filename}")
    except Exception as e:
        print(f"Error creating PDF: {e}")

def main():
    parser = argparse.ArgumentParser(description="Convert an RSS feed to a PDF and email it to your Kindle.")
    parser.add_argument("rss_url", help="The URL of the RSS feed.")
    parser.add_argument("kindle_email", help="Your Kindle email address.")
    parser.add_argument("--sender_email", help="Your email address for sending the file.", default=os.environ.get("SENDER_EMAIL"))
    parser.add_argument("--sender_password", help="Your email password.", default=os.environ.get("SENDER_PASSWORD"))
    parser.add_argument("--output_filename", help="The name of the output PDF file.", default="rss_feed.pdf")
    parser.add_argument("--max_articles", help="The maximum number of articles to process.", type=int, default=10)


    args = parser.parse_args()

    parsed_articles = parse_rss_feed(args.rss_url)

    if parsed_articles:
        articles_with_content = []
        for article in parsed_articles[:args.max_articles]:
            print(f"Processing: {article['title']}")
            content = extract_article_content(article['link'])
            articles_with_content.append({
                'title': article['title'],
                'content': content.replace('\\n', '<br>')
            })

        convert_to_pdf(articles_with_content, args.output_filename)

        if args.sender_email and args.sender_password:
             send_email(
                 args.sender_email,
                 args.sender_password,
                 args.kindle_email,
                 "RSS Feed Content",
                 "Attached is your RSS feed content.",
                 args.output_filename
             )
        else:
            print("\\nEmail sending is skipped. Please provide sender credentials via arguments or environment variables.")

if __name__ == "__main__":
    main()
