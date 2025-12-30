# HTML Template System for Video Processing

This system allows you to create and edit video templates using HTML and CSS, making it much easier to design and customize video overlays compared to writing FFmpeg commands.

## How It Works

1. **HTML Template File** - Design your template using HTML/CSS
2. **Video Placeholder** - Mark where the video should appear
3. **Dynamic Data** - Use placeholders for headline, location, date, etc.
4. **Backend Rendering** - Playwright renders HTML to PNG overlay
5. **Video Compositing** - FFmpeg composites overlay on top of video

## File Structure

```
backend/
├── templates/
│   ├── template1.html        # Full Frame Golden template
│   ├── template2.html        # Split Video Orange template
│   ├── template3.html        # Minimal Modern template
│   ├── template4.html        # Tiruvarur Updates template
│   └── README.md             # This file
├── app/
│   └── services/
│       ├── html_renderer.py  # HTML to PNG rendering service
│       └── video_processor.py # Video processing with templates
```

## Template Structure

### Basic HTML Template

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=1080, height=1920">
    <style>
        body {
            width: 1080px;
            height: 1920px;
            overflow: hidden;
            position: relative;
        }

        /* Video placeholder - transparent area where video shows through */
        .video-placeholder {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: transparent;
            z-index: 1;
        }

        /* Your design elements go here with higher z-index */
    </style>
</head>
<body>
    <!-- Video placeholder must be first -->
    <div class="video-placeholder"></div>

    <!-- Your overlay elements -->
    <div class="headline">{{headline}}</div>
    <div class="location">{{location}}</div>
</body>
</html>
```

## Available Placeholders

Use these placeholders in your HTML, and they will be replaced with actual data:

| Placeholder | Description | Example |
|------------|-------------|---------|
| `{{headline}}` | News headline text | "Breaking: Major Event Happens" |
| `{{location}}` | Location text | "New York, USA" |
| `{{date}}` | Current date (auto-generated) | "30 December 2025" |
| `{{show_location}}` | CSS display value | "block" or "none" |

### Using show_location

To conditionally show/hide location:

```css
.location-container {
    display: {{show_location}};  /* Will be 'block' or 'none' */
}
```

## Design Guidelines

### 1. Fixed Dimensions
- **Width**: 1080px
- **Height**: 1920px (9:16 aspect ratio)
- Always set `overflow: hidden` on body

### 2. Video Placeholder

The video placeholder must:
- Be positioned absolutely
- Have `background: transparent`
- Have `z-index: 1` (lower than overlay elements)
- Cover the area where you want video to show

```css
.video-placeholder {
    position: absolute;
    top: 200px;      /* Start position */
    left: 100px;     /* Start position */
    width: 880px;    /* Video width */
    height: 1200px;  /* Video height */
    background: transparent;
    z-index: 1;
}
```

### 3. Overlay Elements

All overlay elements must:
- Have `z-index: 2` or higher
- Use `position: absolute` for precise placement
- Use semi-transparent backgrounds for better visibility: `rgba(255, 255, 255, 0.95)`

### 4. Text Styling

Best practices for readable text:
- Use `text-shadow` for contrast: `text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.5)`
- Use `box-shadow` for depth: `box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3)`
- Use `backdrop-filter: blur(10px)` for glassmorphism effect

## Template Examples

### Full Screen Video with Text Overlays

```html
<!-- Video takes full screen, text overlays on top -->
<div class="video-placeholder" style="
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: transparent;
    z-index: 1;
"></div>

<div class="top-bar" style="
    position: absolute;
    top: 0;
    width: 100%;
    height: 200px;
    background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
    z-index: 2;
"></div>
```

### Split Screen Video

```html
<!-- Video in center, design elements around it -->
<div class="video-placeholder" style="
    position: absolute;
    top: 200px;
    left: 100px;
    width: 880px;
    height: 1200px;
    background: transparent;
    border: 4px solid #ff6b35;
    border-radius: 15px;
    z-index: 1;
"></div>
```

## Using HTML Templates in Code

### Python Usage

```python
from app.services.video_processor import VideoProcessor

# Process video with HTML template
success = VideoProcessor.process_with_html_template(
    input_path="input.mp4",
    output_path="output.mp4",
    template_name="template1.html",  # HTML template file
    headline="Breaking News: Important Event",
    location="New York, USA",
    show_location=True
)
```

### Workflow

1. **Render HTML to PNG**
   - Playwright opens headless Chromium browser
   - Loads HTML template
   - Replaces placeholders with actual data
   - Takes screenshot → transparent PNG overlay

2. **Process Video**
   - FFmpeg converts video to 9:16 format
   - Crops/scales video to fit placeholder area
   - Composites PNG overlay on top

3. **Add Audio**
   - Preserves original audio from source video
   - Fallback to video-only if audio processing fails

## Creating a New Template

1. **Create HTML file** in `backend/templates/` folder

```bash
cd backend/templates
touch template5.html
```

2. **Design your template**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=1080, height=1920">
    <style>
        /* Your CSS here */
    </style>
</head>
<body>
    <div class="video-placeholder"></div>
    <!-- Your design elements -->
</body>
</html>
```

3. **Use placeholders** for dynamic content

```html
<h1>{{headline}}</h1>
<p>{{location}}</p>
```

4. **Test your template**

```python
VideoProcessor.process_with_html_template(
    input_path="test.mp4",
    output_path="output.mp4",
    template_name="template5.html",
    headline="Test Headline",
    location="Test Location"
)
```

## Advantages of HTML Templates

### ✅ Easier to Edit
- Visual HTML/CSS editing vs complex FFmpeg commands
- Use browser DevTools to preview (set viewport to 1080x1920)
- Quick iteration on design

### ✅ More Flexible
- Any CSS effect: gradients, shadows, animations, borders
- Complex layouts: flexbox, grid, absolute positioning
- Custom fonts, icons, images

### ✅ Reusable
- Same template with different data
- Share templates across projects
- Version control friendly

### ✅ Designer Friendly
- No FFmpeg knowledge required
- Standard web technologies
- Preview in browser before rendering

## Browser Preview

To preview your template in a browser:

1. Open the HTML file in Chrome/Firefox
2. Open DevTools (F12)
3. Toggle device toolbar (Ctrl+Shift+M)
4. Set custom dimensions: 1080 x 1920
5. Edit and refresh to see changes

## Troubleshooting

### Template not rendering

**Issue**: HTML template renders as blank
- **Solution**: Check that `video-placeholder` has `background: transparent`

### Text not visible

**Issue**: Text appears but is not readable over video
- **Solution**: Add `text-shadow` or semi-transparent background box

### Video not showing through

**Issue**: Video is completely hidden
- **Solution**: Ensure overlay elements have `z-index` higher than video placeholder

### Fonts not loading

**Issue**: Custom fonts don't appear in rendered video
- **Solution**: Use system fonts or embed fonts with `@font-face` and data URIs

## Performance Notes

- HTML rendering adds ~2-3 seconds to processing time
- Playwright uses headless Chromium (downloads automatically on first run)
- Temporary PNG overlay is deleted after compositing
- Falls back to FFmpeg-based templates if HTML rendering fails

## Installation

1. Install Playwright:

```bash
pip install playwright
playwright install chromium
```

2. The system will automatically use HTML templates when `process_with_html_template()` is called

## Next Steps

- Customize existing templates
- Create new templates for different news styles
- Add logo images to templates
- Experiment with CSS animations (note: rendered as static image)
- Share your templates with others
