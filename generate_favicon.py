from PIL import Image, ImageDraw

# Create a simple chart icon
size = (32, 32)
img = Image.new('RGBA', size, (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Draw a simple upward trend line
points = [(5, 25), (10, 20), (15, 22), (20, 15), (25, 18), (30, 10)]
draw.line(points, fill=(40, 167, 69), width=2)  # Bootstrap success green

# Draw axes
draw.line([(5, 27), (30, 27)], fill=(108, 117, 125), width=1)  # Gray
draw.line([(5, 27), (5, 5)], fill=(108, 117, 125), width=1)

img.save('app/static/favicon.ico')
print("✅ Favicon created at app/static/favicon.ico")
