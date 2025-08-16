

import requests
from bs4 import BeautifulSoup
import json
from groq import Groq
import os
from urllib.parse import urljoin
import re


def extract_text_from_html(html_content: str) -> str:
    """
    Parses HTML and extracts the text from the main content area,
    stripping out navigation, footers, scripts, etc.
    """
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, "html.parser")
    
    
    for tag in soup(['nav', 'header', 'footer', 'script', 'style']):
        tag.decompose()
    
    
    main_content = soup.find('main') or soup.find(role='main')
    
    if main_content:
        return main_content.get_text(separator='\n', strip=True)
    
    
    return soup.body.get_text(separator='\n', strip=True) if soup.body else ""

# --- Scraper Functions ---
def get_website_content(url: str):
    """Fetches the HTML content of a given URL, pretending to be a browser."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, timeout=15, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching website content for {url}: {e}")
        return None

def get_products(website_url: str):
    """Fetches the full product catalog, gracefully handling 404/403 errors."""
    products_url = urljoin(website_url, "/products.json")
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(products_url, timeout=15, headers=headers)
        response.raise_for_status()
        return response.json().get("products", [])
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error fetching products for {website_url} (This is common for non-Shopify or protected sites): {http_err}")
        return []
    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        print(f"Error fetching products for {website_url}: {e}")
        return []

def get_hero_products(soup, base_url: str):
    """Extracts products listed on the homepage."""
    hero_products = []
    product_links = set()
    for link in soup.select('a[href*="/products/"]'):
        product_url = urljoin(base_url, link['href'])
        if product_url in product_links or '/collections/' in product_url or '?variant=' in product_url:
            continue
        title_element = link.find(['h2', 'h3', 'p'], class_=re.compile(r'title|heading', re.I))
        title = title_element.get_text(strip=True) if title_element else link.get_text(strip=True)
        if title:
            hero_products.append({"title": title, "url": product_url})
            product_links.add(product_url)
    return hero_products

def get_social_handles(soup):
    """Finds social media links on the page."""
    social_handles = {}
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if "instagram.com" in href and "instagram" not in social_handles: social_handles["instagram"] = href
        if "facebook.com" in href and "facebook" not in social_handles: social_handles["facebook"] = href
        if "tiktok.com" in href and "tiktok" not in social_handles: social_handles["tiktok"] = href
        if "youtube.com" in href and "youtube" not in social_handles: social_handles["youtube"] = href
        if ("twitter.com" in href or "x.com" in href) and "twitter" not in social_handles: social_handles["twitter"] = href
    return social_handles

def get_contact_details(soup):
    """Finds contact email and phone number."""
    contact_details = {}
    page_text = soup.get_text()
    mailto_link = soup.find('a', href=re.compile(r'mailto:'))
    if mailto_link:
        contact_details['email'] = mailto_link['href'].replace('mailto:', '').strip()
    else:
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.[\w]+', page_text)
        if email_match:
            contact_details['email'] = email_match.group(0)
    tel_link = soup.find('a', href=re.compile(r'tel:'))
    if tel_link:
        contact_details['phone'] = tel_link['href'].replace('tel:', '').strip()
    else:
        phone_match = re.search(r'(\+?\d{1,3}[\s-]?\(?\d{2,3}\)?[\s-]?\d{3}[\s-]?\d{4})', page_text)
        if phone_match:
            contact_details['phone'] = phone_match.group(0)
    return contact_details

def get_brand_context(soup, base_url: str):
    """Finds and scrapes the 'About Us' page."""
    about_us_text = ""
    about_us_page = soup.find("a", string=re.compile(r'about|story', re.I))
    if about_us_page and about_us_page.has_attr('href'):
        about_us_url = urljoin(base_url, about_us_page['href'])
        about_us_content_html = get_website_content(about_us_url)
        if about_us_content_html:
            
            about_us_text = extract_text_from_html(about_us_content_html)
    return about_us_text

def get_important_links(soup, base_url):
    """Finds key navigation links."""
    important_links = {}
    nav_areas = soup.find_all(['nav', 'footer'])
    for area in nav_areas:
        for link in area.find_all("a", href=True):
            href = urljoin(base_url, link["href"])
            text = link.text.strip().lower()
            if "track" in text and "order_tracking" not in important_links: important_links["order_tracking"] = href
            if "contact" in text and "contact_us" not in important_links: important_links["contact_us"] = href
            if "blog" in text and "blogs" not in important_links: important_links["blogs"] = href
            if "privacy" in text and "privacy_policy" not in important_links: important_links["privacy_policy"] = href
            if ("return" in text or "refund" in text) and "return_policy" not in important_links: important_links["return_policy"] = href
            if "faq" in text and "faqs" not in important_links: important_links["faqs"] = href
    return important_links

def get_faqs_from_page(faq_url: str):
    """Scrapes a dedicated FAQ page by parsing its HTML structure for common patterns."""
    faq_html = get_website_content(faq_url)
    if not faq_html: return []
    soup = BeautifulSoup(faq_html, 'html.parser')
    faqs = []
    for item in soup.find_all('details'):
        question_tag = item.find('summary')
        answer_container = item.find('div') or item.find('p')
        if question_tag and answer_container:
            question = question_tag.get_text(strip=True)
            answer = answer_container.get_text(strip=True)
            if question and answer:
                faqs.append({"question": question, "answer": answer})
    return faqs

def get_groq_response(prompt, content):
    """Sends content to Groq for analysis."""
    try:
        client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        completion = client.chat.completions.create(
            model="compound-beta",
            messages=[{"role": "user", "content": f"{prompt}\n\nContent:\n{content}"}],
            temperature=0, max_tokens=2048, top_p=1, stream=False, stop=None,
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Error with Groq API: {e}")
        return ""

def get_brand_data(website_url: str):
    """Main function to orchestrate the data scraping."""
    content = get_website_content(website_url)
    if not content: return None
    soup = BeautifulSoup(content, "html.parser")
    
    full_product_catalog = get_products(website_url)
    simplified_product_catalog = [
        {"title": p.get("title"), "url": urljoin(website_url, f"/products/{p.get('handle')}"), "price": p.get("variants", [{}])[0].get("price", "N/A"), "main_image_url": p.get("images", [{}])[0].get("src")}
        for p in full_product_catalog
    ]

    hero_products = get_hero_products(soup, website_url)
    social_handles = get_social_handles(soup)
    important_links = get_important_links(soup, website_url)
    contact_details = get_contact_details(soup)
    brand_context = get_brand_context(soup, website_url)
    
    privacy_policy, return_policy, faqs = "", "", []

    if important_links.get("privacy_policy"):
        policy_html = get_website_content(important_links["privacy_policy"])
        policy_text = extract_text_from_html(policy_html)
        if policy_text:
            prompt = "Extract and return only the text of the privacy policy from the content below."
            privacy_policy = get_groq_response(prompt, policy_text[:3500]) # Truncate content

    if important_links.get("return_policy"):
        policy_html = get_website_content(important_links["return_policy"])
        policy_text = extract_text_from_html(policy_html)
        if policy_text:
            prompt = "Extract and return only the text of the return and refund policy from the content below."
            return_policy = get_groq_response(prompt, policy_text[:3500]) # Truncate content
            
    if important_links.get("faqs"):
        # First, try direct scraping for structured FAQs
        faqs = get_faqs_from_page(important_links["faqs"])
        
        # If direct scraping fails, fall back to the LLM
        if not faqs:
            print("Direct FAQ scraping failed, falling back to LLM.")
            faq_html = get_website_content(important_links["faqs"])
            faq_text = extract_text_from_html(faq_html)
            if faq_text:
                prompt = "Extract FAQs from the following text. Return a valid JSON array where each object has a 'question' and 'answer' key. If no FAQs are found, return an empty array []."
                faqs_json_str = get_groq_response(prompt, faq_text[:3500]) # Truncate content
                if faqs_json_str:
                    try:
                        json_match = re.search(r'\[.*\]', faqs_json_str, re.DOTALL)
                        if json_match:
                            faqs = json.loads(json_match.group())
                    except json.JSONDecodeError:
                        print(f"Failed to parse FAQs from Groq response: {faqs_json_str}")

    return {
        "product_catalog": simplified_product_catalog, "hero_products": hero_products,
        "privacy_policy": privacy_policy, "return_policy": return_policy, "faqs": faqs,
        "social_handles": social_handles, "contact_details": contact_details,
        "brand_context": brand_context, "important_links": important_links,
    }