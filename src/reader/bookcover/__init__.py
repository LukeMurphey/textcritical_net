import os
import tempfile
import random

from wand.drawing import Drawing
from wand.image import Image
from wand.color import Color

def splitTextIntoMultipleLines(text, max_line_length):

    words = text.split(' ')

    line = ''
    new_text = ''

    for word in words:

        if len(line + word) > max_line_length:
            new_text = new_text + line + '\n'

            line = word
        elif len(line) > 0:
            line = line + ' ' + word
        else:
            line = word

    # Handle leftovers
    new_text = new_text + line

    return new_text

def makeCoverImage(work, filename=None, width=None):

    if filename is None:
        tmpdir = tempfile.mkdtemp()
        randomfilename = "Book_Cover_" + str(random.randrange(0, 1000000000000, 20)) + ".png"
        filename = os.path.join(tmpdir, randomfilename)

    # Make a decision regarding what size the make the title
    if len(work.title) > 30:
        title_font_size = 35
        max_title_length = 24
    elif len(work.title) > 24:
        title_font_size = 50
        max_title_length = 18
    else:
        title_font_size = 75
        max_title_length = 10

    # Determine which background image to use
    if work.language == "Greek":
        bg_image = 'media/images/epub/Book_Cover.png'
    else:
        bg_image = 'media/images/epub/Book_Cover_Grey.png'

    # Process the title to fit onto multiple lines if necessary
    title = splitTextIntoMultipleLines(work.title, max_title_length).strip()

    # Make the cover image
    with Drawing() as draw:
        with Image(filename=bg_image) as image:
            with Color('white') as white:

                # Draw the title
                draw.font = 'media/font/epub/Heuristica-Regular.otf'
                draw.font_size = title_font_size
                draw.fill_color = white
                draw.text_alignment = 'center'
                draw.text(round(image.width / 2), 250, title)
                draw.text_antialias = True
                draw.text_interword_spacing = 10
                draw(image)

            with Color('#ffb800') as yellow:

                authors = '\n'.join(work.authors.filter(meta_author=False).values_list('name', flat=True))

                if authors and len(authors) > 0:
                    #   Draw the author
                    draw.font = 'media/font/epub/Heuristica-Bold.otf'
                    draw.font_size = 36
                    draw.fill_color = yellow
                    draw.text_alignment = 'center'
                    draw.text(round(image.width / 2), 500, authors)
                    draw.text_kerning = 140.0
                    draw(image)

            # Adjust the image height if necessary
            if width is not None:

                # Make the number a float so that the math doesn't result in a division by zero
                # based on integers losing the value of the decimal points
                width = width * 1.0
                new_height = image.size[1] / (image.size[0] / width)

                # Convert the numbers back to integers since wand wants integers
                width = int(width)
                new_height = int(new_height)

                # Resize the image
                image.resize(width, new_height)

            # Save the image to the file
            image.save(filename=filename)

    return filename
