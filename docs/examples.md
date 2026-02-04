# Examples

Real-world usage examples for RustMatch.

## UI Automation

### Click on Button

```python
import rustmatch
import pyautogui
from PIL import ImageGrab

def click_button(button_image_path, confidence=0.8):
    """Find and click a button on screen."""
    # Capture screen and save temporarily
    screen = ImageGrab.grab()
    screen.save("_temp_screen.png")
    
    # Get template size
    tpl_w, tpl_h = rustmatch.get_size(button_image_path)
    
    # Find button
    result = rustmatch.find("_temp_screen.png", button_image_path, threshold=confidence)
    
    if result:
        # Click center of button
        center_x = result.x + tpl_w // 2
        center_y = result.y + tpl_h // 2
        pyautogui.click(center_x, center_y)
        return True
    return False

# Usage
click_button("login_button.png")
```

### Wait for Element

```python
import rustmatch
import time
from PIL import ImageGrab

def wait_for_element(template_path, timeout=10, interval=0.5):
    """Wait for an element to appear on screen."""
    start = time.time()
    
    while time.time() - start < timeout:
        # Capture screen
        screen = ImageGrab.grab()
        screen.save("_temp_screen.png")
        
        result = rustmatch.find("_temp_screen.png", template_path, threshold=0.85)
        if result:
            return result
        
        time.sleep(interval)
    
    return None
```

## Game Bot

### Find Multiple Items

```python
import rustmatch

def find_items(screen_path, item_path, max_items=10):
    """Find all instances of an item on screen."""
    results = rustmatch.find_all(
        screen_path, 
        item_path,
        threshold=0.8,
        max_count=max_items
    )
    
    return [(r.x, r.y, r.confidence) for r in results]

# Find all gold coins
coins = find_items("game_screen.png", "gold_coin.png")
print(f"Found {len(coins)} coins")
```

### Using Bytes for Speed

```python
import rustmatch
from PIL import ImageGrab
import io

def find_on_screen_fast(template_path):
    """Fast screen matching using bytes."""
    # Capture screen to bytes (no file I/O)
    screen = ImageGrab.grab()
    buffer = io.BytesIO()
    screen.save(buffer, format='PNG')
    screen_bytes = buffer.getvalue()
    
    # Load template bytes
    with open(template_path, "rb") as f:
        template_bytes = f.read()
    
    # Match
    return rustmatch.find_bytes(screen_bytes, template_bytes, threshold=0.8)
```

## Visualization

### Draw All Matches

```python
import rustmatch
from PIL import Image, ImageDraw

def visualize_matches(source_path, template_path, output_path):
    """Draw all matches on image and save."""
    # Find matches
    results = rustmatch.find_all(source_path, template_path, threshold=0.7, max_count=20)
    
    # Load original image
    img = Image.open(source_path)
    draw = ImageDraw.Draw(img)
    
    # Get template size
    tw, th = rustmatch.get_size(template_path)
    
    # Draw rectangles
    for r in results:
        color = "green" if r.confidence > 0.9 else "yellow"
        draw.rectangle(
            [r.x, r.y, r.x + tw, r.y + th],
            outline=color, width=2
        )
        draw.text(
            (r.x, r.y - 15),
            f"{r.confidence:.0%}",
            fill=color
        )
    
    img.save(output_path)
    print(f"Saved visualization to {output_path}")

visualize_matches("screen.png", "icon.png", "result.png")
```

## Batch Processing

### Process Multiple Screenshots

```python
import rustmatch
import os

def batch_find(screenshot_dir, template_path, output_file):
    """Find template in multiple screenshots."""
    results = []
    
    for filename in os.listdir(screenshot_dir):
        if filename.endswith(('.png', '.jpg', '.jpeg')):
            filepath = os.path.join(screenshot_dir, filename)
            result = rustmatch.find(filepath, template_path, threshold=0.8)
            
            if result:
                results.append({
                    'file': filename,
                    'x': result.x,
                    'y': result.y,
                    'confidence': result.confidence
                })
    
    # Save results
    with open(output_file, 'w') as f:
        for r in results:
            f.write(f"{r['file']}: ({r['x']}, {r['y']}) - {r['confidence']:.2%}\n")
    
    return results
```
