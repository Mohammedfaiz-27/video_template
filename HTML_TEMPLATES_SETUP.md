# HTML Template System - Setup Guide

## Quick Start

The HTML template system allows you to design video templates using HTML/CSS instead of complex FFmpeg commands.

### Installation

1. **Install Playwright** (for HTML rendering):

```bash
cd backend
pip install -r requirements.txt
playwright install chromium
```

This will:
- Install the Playwright library
- Download Chromium browser (headless, for rendering HTML)
- Install all other dependencies

### How to Use HTML Templates

#### Option 1: Use Existing Templates

All 4 templates now have HTML versions in `backend/templates/`:

- `template1.html` - Full Frame Golden
- `template2.html` - Split Video Orange
- `template3.html` - Minimal Modern
- `template4.html` - Tiruvarur Updates

To use HTML templates in your code, call the new method:

```python
from app.services.video_processor import VideoProcessor

# Using HTML template instead of FFmpeg-based template
success = VideoProcessor.process_with_html_template(
    input_path="input_video.mp4",
    output_path="output_video.mp4",
    template_name="template4.html",  # HTML file name
    headline="Breaking: Major News Event",
    location="Tiruvarur, Tamil Nadu",
    show_location=True
)
```

#### Option 2: Create Your Own Template

1. **Create new HTML file** in `backend/templates/` folder:

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
            background: #ffffff;
        }

        /* Video shows through transparent area */
        .video-placeholder {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: transparent;
            z-index: 1;
        }

        /* Your custom design elements */
        .my-headline {
            position: absolute;
            bottom: 200px;
            left: 60px;
            right: 60px;
            background: rgba(0, 0, 0, 0.9);
            color: white;
            padding: 40px;
            font-size: 48px;
            z-index: 2;
        }
    </style>
</head>
<body>
    <div class="video-placeholder"></div>
    <div class="my-headline">{{headline}}</div>
</body>
</html>
```

2. **Use placeholders** for dynamic content:
   - `{{headline}}` - Your news headline
   - `{{location}}` - Location text
   - `{{date}}` - Auto-generated current date
   - `{{show_location}}` - "block" or "none" (for conditional visibility)

3. **Preview in browser** (optional):
   - Open HTML file in Chrome
   - Press F12 → Toggle device toolbar (Ctrl+Shift+M)
   - Set dimensions to 1080 x 1920
   - Replace placeholders with sample text

4. **Use your template**:

```python
VideoProcessor.process_with_html_template(
    input_path="input.mp4",
    output_path="output.mp4",
    template_name="my_custom_template.html",
    headline="My Custom Headline",
    location="My Location"
)
```

### Updating Existing Templates

Simply edit the HTML files in `backend/templates/` folder:

```bash
# Edit template
code backend/templates/template4.html

# Changes take effect immediately - no need to restart server
```

### Why Use HTML Templates?

| FFmpeg Commands | HTML Templates |
|----------------|----------------|
| Complex filter syntax | Simple HTML/CSS |
| Hard to visualize | Preview in browser |
| Difficult to position text | Drag & drop with CSS |
| Limited styling | All CSS features |
| Requires FFmpeg knowledge | Standard web dev |

### Example: Editing Template 4

**Before** (FFmpeg commands in Python):
```python
stream = ffmpeg.filter(stream, 'drawbox', x=20, y=20, width='iw-40', height=300, color='#8b2500@0.95', thickness='fill')
stream = ffmpeg.filter(stream, 'drawtext', text='TIRUVARUR\\nUPDATES', fontfile='arial.ttf', ...)
```

**After** (HTML/CSS):
```html
<div style="
    position: absolute;
    top: 20px;
    left: 20px;
    right: 20px;
    height: 300px;
    background: linear-gradient(180deg, #c43b00 0%, #8b2500 100%);
">
    <div style="font-size: 28px; color: white;">
        TIRUVARUR<br>UPDATES
    </div>
</div>
```

Much easier to understand and edit!

### Integration with Backend

The system automatically:

1. ✅ Renders HTML to transparent PNG overlay
2. ✅ Converts video to 9:16 format
3. ✅ Composites overlay on video
4. ✅ Preserves original audio
5. ✅ Falls back to FFmpeg templates if HTML fails

### Fallback Behavior

If HTML rendering fails (Playwright not installed, template error, etc.), the system will:
- Log a warning
- Automatically fall back to FFmpeg-based templates
- Continue processing without interruption

### File Structure

```
backend/
├── templates/
│   ├── template1.html        ← Edit these files
│   ├── template2.html
│   ├── template3.html
│   ├── template4.html
│   └── README.md             ← Detailed template guide
├── app/
│   └── services/
│       ├── html_renderer.py  ← HTML rendering service
│       └── video_processor.py ← Video processing
└── requirements.txt          ← Updated with playwright
```

### Common Issues

**Q: Playwright installation fails**
```bash
# Try manual installation
pip install playwright==1.41.0
python -m playwright install chromium
```

**Q: Templates not rendering**
- Check that HTML file exists in `backend/templates/`
- Verify file name matches (case-sensitive)
- Check browser console for errors when previewing

**Q: Video not visible**
- Ensure `.video-placeholder` has `background: transparent`
- Check z-index values (video should be lowest)

**Q: Text looks different in output vs browser**
- Some fonts may not be available in headless browser
- Use web-safe fonts or embed fonts with @font-face

### Next Steps

1. ✅ Install dependencies: `pip install -r requirements.txt && playwright install chromium`
2. ✅ Edit HTML templates in `backend/templates/`
3. ✅ Preview in browser (1080x1920 viewport)
4. ✅ Test with your videos
5. ✅ Create custom templates for your brand

### Need Help?

- See `backend/templates/README.md` for detailed template documentation
- Check existing templates for examples
- Test templates in browser before using with videos

---

**That's it!** You can now create and edit video templates using HTML/CSS instead of FFmpeg commands.
