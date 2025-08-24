from PIL import Image

# Define colors in RGB
colors = {
    'red': (255, 0, 0),
    'blue': (0, 0, 255),
    'green': (0, 255, 0),
    'aqua': (0, 255, 255),
    'brown': (165, 42, 42),
    'black': (0, 0, 0)
}

def create_colored_png(color_name):
    color = colors.get(color_name.lower())
    if not color:
        raise ValueError(f"Color '{color_name}' not supported.")
    filename = f"images/{color_name}-{color[0]}-{color[1]}-{color[2]}.png"
    img = Image.new('RGB', (32, 32), color)
    img.save(filename, 'PNG')

# Example usage:
create_colored_png('red')
create_colored_png('blue')
create_colored_png('green')
create_colored_png('aqua')
create_colored_png('brown')
create_colored_png('black')