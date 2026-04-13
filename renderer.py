import json
import os
from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright
import time

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")

def render_html_to_png(html_content, output_path, width, height):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": width, "height": height})
        page.set_content(html_content)
        # Wait for web fonts to load
        page.evaluate('document.fonts.ready')
        # Wait a tiny bit extra to ensure SVGs or slow fonts render
        page.wait_for_timeout(500)
        page.screenshot(path=output_path)
        browser.close()

def generate_all_images(brand_data, social_data):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    
    generated_files = []
    
    # 1. Blog Header (Standard 1200x630)
    header_template = env.get_template("blog_header.html")
    header_html = header_template.render(brand=brand_data, title=social_data['blog_header_title'])
    header_path = os.path.join(OUTPUT_DIR, "blog_header.png")
    render_html_to_png(header_html, header_path, 1200, 630)
    generated_files.append(header_path)
    
    # 2. Carousel Slides (Standard Instagram 1080x1080)
    carousel_template = env.get_template("carousel_slide.html")
    for i, slide_title in enumerate(social_data['carousel_slides_titles']):
        slide_html = carousel_template.render(
            brand=brand_data, 
            title=slide_title, 
            slide_num=f"{i+1}/{len(social_data['carousel_slides_titles'])}"
        )
        slide_path = os.path.join(OUTPUT_DIR, f"carousel_slide_{i+1}.png")
        render_html_to_png(slide_html, slide_path, 1080, 1080)
        generated_files.append(slide_path)
        
    return generated_files
