import os
import sys
import asyncio
from playwright.async_api import async_playwright
import re

async def render_mermaid(input_file):
    base_name = os.path.splitext(input_file)[0]
    png_path = f"{base_name}.png"
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract mermaid block if it's a markdown file
    if input_file.endswith('.md'):
        match = re.search(r'```mermaid\n(.*?)\n```', content, re.DOTALL)
        if match:
            mmd_content = match.group(1)
        else:
            print(f"No mermaid block found in {input_file}")
            return
    else:
        mmd_content = content

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ background: transparent; padding: 20px; margin: 0; }}
            .mermaid {{ display: inline-block; }}
        </style>
    </head>
    <body>
        <div class="mermaid">
{mmd_content}
        </div>
        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            mermaid.initialize({{ 
                startOnLoad: true, 
                theme: 'base',
                themeVariables: {{
                    primaryColor: '#e1f5fe',
                    primaryBorderColor: '#0288d1',
                    lineColor: '#333333',
                    fontFamily: 'Inter, sans-serif'
                }}
            }});
        </script>
    </body>
    </html>
    """
    
    html_path = f"{base_name}.html"
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    print(f"Loading HTML in Playwright for {input_file}...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # 4x scaling for HD Resolution
        page = await browser.new_page(device_scale_factor=4)
        
        await page.goto(f"file:///{os.path.abspath(html_path)}")
        
        await page.wait_for_selector("div.mermaid > svg", state="visible", timeout=15000)
        await page.wait_for_timeout(1000)
        
        svg_element = await page.query_selector("div.mermaid > svg")
        
        if svg_element:
            bounding_box = await svg_element.bounding_box()
            await page.set_viewport_size({
                "width": int(bounding_box["width"]) + 64,
                "height": int(bounding_box["height"]) + 64
            })
            
            await svg_element.screenshot(path=png_path, omit_background=True)
            print(f"Successfully rendered HD Mermaid PNG to {png_path}")
        else:
            print("Failed to find SVG element.")
            
        await browser.close()
        
    try:
        os.remove(html_path)
    except:
        pass

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python render_c4.py <file.md>")
        sys.exit(1)
    asyncio.run(render_mermaid(sys.argv[1]))
