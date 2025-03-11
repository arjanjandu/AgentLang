# game_generator.py
import os
import re
import webbrowser
from pathlib import Path
from html.parser import HTMLParser
from dotenv import load_dotenv
from openai import OpenAI
from typing import Tuple

# Load environment variables from .env file
load_dotenv()

# Initialize the OpenAI client using the API key from .env
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

class HTMLValidator(HTMLParser):
    """Simple HTML parser to check for basic validity and count <script> tags."""
    def __init__(self):
        super().__init__()
        self.script_count = 0
        self.errors = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "script":
            self.script_count += 1

    def error(self, message):
        self.errors.append(message)

def refine_game_prompt(user_input: str, retry: bool = False) -> str:
    """Refine the user's game idea into a detailed HTML game prompt."""
    base_prompt = f"""
    Create a complete HTML game based on the following user request: '{user_input}'
    
    Additional requirements:
    1. The game must be fully functional in modern browsers (Chrome, Firefox, etc.).
    2. Use HTML5, CSS, and JavaScript.
    3. Include onscreen buttons for mobile as well as key controls for PC.
    4. Implement a basic scoring system, game over state, and restart option.
    5. Write clean, well-commented code with consistent indentation.
    6. Use simple CSS colors and shapes (e.g., rectangles, circles) instead of images for visuals.
    7. Use a single <script> tag to contain all game logic.
    8. Ensure the code is performant and free of syntax errors.
    Provide the complete code including the <!DOCTYPE html>, <html>, <head>, and <body> tags.
    """
    if retry:
        base_prompt += "\n\nNote: Previous attempt had issues. Ensure one <script> tag and valid HTML."
    return base_prompt.strip()

def generate_game_html(prompt: str) -> str:
    """Generate HTML game code using OpenAI's API."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert HTML5 game developer."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4000,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating game: {str(e)}"

def extract_html_content(raw_content: str) -> str:
    """Extracts HTML code from the API response."""
    if "```html" in raw_content and "```" in raw_content:
        start = raw_content.index("```html") + len("```html")
        end = raw_content.rindex("```")
        return raw_content[start:end].strip()
    return raw_content.strip()

def validate_html(html_content: str) -> Tuple[bool, str]:
    """Validate HTML content for structure and single script tag."""
    validator = HTMLValidator()
    try:
        validator.feed(html_content)
        if validator.script_count > 1:
            return False, "Multiple script tags detected."
        if not re.search(r"<!DOCTYPE html>", html_content, re.IGNORECASE) or \
           not re.search(r"<html", html_content, re.IGNORECASE) or \
           not re.search(r"</html>", html_content, re.IGNORECASE):
            return False, "Missing essential HTML structure."
        return True, "Basic validation passed."
    except Exception as e:
        return False, f"HTML parsing error: {str(e)}"

def refine_html_content(html_content: str) -> str:
    """Send HTML back to LLM for final review and improvement."""
    refine_prompt = f"""
    Review and improve the following HTML game code:
    
    {html_content}
    
    Ensure:
    1. Full functionality and browser compatibility.
    2. Optimized JavaScript for performance.
    3. Enhanced CSS for visuals (no images).
    4. Fixed syntax errors or inconsistencies.
    5. Single <script> tag and valid HTML structure.
    6. Clear, improved comments.
    Return the complete, improved HTML code.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert HTML5 game developer and code reviewer."},
                {"role": "user", "content": refine_prompt}
            ],
            max_tokens=4000,
            temperature=0.5
        )
        return extract_html_content(response.choices[0].message.content)
    except Exception as e:
        print(f"Error refining HTML: {str(e)}")
        return html_content

def save_game_file(game_name: str, html_content: str) -> str:
    """Saves HTML content to a file with a safe filename."""
    safe_name = "".join(c for c in game_name if c.isalnum() or c in " -_").strip()
    filename = f"{safe_name.lower().replace(' ', '_')}.html"
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(html_content)
        return filename
    except Exception as e:
        return f"Error saving file: {str(e)}"

def make_game(game_idea: str, open_browser: bool = True) -> str:
    """Generate an HTML game, save it, and open it in the browser if successful."""
    if not game_idea.strip():
        return "Error: No game idea provided."

    game_name = game_idea.split()[0] + "_game"
    max_attempts = 3
    html_content = ""

    for attempt in range(max_attempts):
        prompt = refine_game_prompt(game_idea, retry=(attempt > 0))
        raw_output = generate_game_html(prompt)
        if raw_output.startswith("Error"):
            return raw_output
        
        html_content = extract_html_content(raw_output)
        valid, message = validate_html(html_content)
        print(f"Attempt {attempt + 1}: {message}")
        
        if valid:
            break
        if attempt == max_attempts - 1:
            return "Error: Failed to generate valid HTML after multiple attempts."

    enhanced_html = refine_html_content(html_content)
    valid, message = validate_html(enhanced_html)
    if not valid:
        print(f"Warning: Refined HTML failed - {message}. Using original.")
        enhanced_html = html_content
    
    filename = save_game_file(game_name, enhanced_html)
    if "Error" not in filename and open_browser:
        webbrowser.open(f"file://{Path(filename).absolute()}")
        return "Successfully created game"
    return filename

if __name__ == "__main__":
    idea = input("Enter your game idea: ").strip()
    result = make_game(idea)
    print(result)