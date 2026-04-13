import os
import json
from google import genai
from google.genai import types
from pydantic import BaseModel

def get_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise Exception("Gemini Client not initialized. Did you set GEMINI_API_KEY in the sidebar?")
    return genai.Client(api_key=api_key)

class SocialContent(BaseModel):
    instagram_caption: str
    linkedin_post: str
    twitter_posts: list[str]
    blog_header_title: str
    carousel_slides_titles: list[str]

def generate_blog(topic: str) -> str:
    client = get_client()
        
    prompt = f"Write a comprehensive, engaging, SEO-optimized blog post about the Web3/Crypto topic: {topic}. Use professional but accessible language. Keep it between 500-800 words, using Markdown formatting."
    response = client.models.generate_content(
        model='gemini-1.5-flash',
        contents=prompt,
    )
    return response.text

def generate_social_assets(blog_text: str) -> dict:
    client = get_client()
        
    prompt = f"""Based on the following blog post, extract and create social media content:
1. An Instagram caption with relevant hashtags.
2. An engaging LinkedIn text post.
3. 2-3 engaging Twitter posts (threads or individual).
4. A short, punchy title for the Blog Header graphic.
5. Provide 4 to 6 short, punchy statements (max 10 words each) to be used as individual text overlays for an Instagram carousel graphic series that summarizes the blog.

Blog Post:
{blog_text}
"""
    response = client.models.generate_content(
        model='gemini-1.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=SocialContent,
            temperature=0.7,
        ),
    )
    return json.loads(response.text)
