ICON CREATION INSTRUCTIONS
=========================

You need to create PNG icons in the following sizes and place them in /static/icons/:

Required Icons:
- icon-72x72.png
- icon-96x96.png  
- icon-128x128.png
- icon-144x144.png
- icon-152x152.png
- icon-192x192.png
- icon-384x384.png
- icon-512x512.png

QUICK OPTION - Use an online PWA icon generator:
1. Go to https://www.pwabuilder.com/imageGenerator
2. Upload a base image (512x512 recommended)
3. Download the generated icon pack
4. Copy the icons to /static/icons/ folder

MANUAL OPTION - Create simple icons:
1. Create a 512x512 image with:
   - Blue background (#0d6efd)
   - White text "MME" in center
   - Rounded corners (optional)
2. Use image editing software to resize to all required sizes
3. Save as PNG files with exact names listed above

TEMPORARY WORKAROUND:
For testing, you can use any square PNG images renamed to the correct filenames.
The app will still work as a PWA even with placeholder icons.