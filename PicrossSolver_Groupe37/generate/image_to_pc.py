from PIL import Image
import numpy as np
import sys

DIMENSIONS = 32
THRESHOLD = 128


def main():
    if len(sys.argv) != 3:
        raise ValueError("Usage: python image_to_pc.py <image> <dim>")

    # Open an image
    img = Image.open(sys.argv[1])

    DIMENSIONS = int(sys.argv[2])

    # Ensure height equals width
    if img.width != img.height:
        raise ValueError("Image must be square")

    # Crop image so size if multiple of DIMENSIONS
    new_size = img.width - (img.width % DIMENSIONS)
    img = img.crop((0, 0, new_size, new_size))

    # Build blocks
    blocks = createBlocks(img)
    file = sys.argv[1].split("/")[-1]
    filename = file.split(".")[0]
    writeBlocksToFile(blocks, filename)
    writeSolution(blocks, filename)


def createBlocks(img):
    pixels = img.load()
    block_size = img.width // DIMENSIONS

    # Init numpy array representing blocks
    blocks = np.zeros((DIMENSIONS, DIMENSIONS))

    grayscale = isinstance(pixels[0, 0], int)

    # Iterate over blocks
    for i in range(0, img.width, block_size):
        for j in range(0, img.height, block_size):
            # Iterate over pixels in block
            avg = 0
            for x in range(i, i + block_size):
                for y in range(j, j + block_size):
                    a = pixels[x, y]

                    if grayscale:
                        if a > THRESHOLD:
                            avg += 1
                    else:
                        a = a[0]
                    if a > THRESHOLD:
                        avg += 1

            # Color pixel depending on average of pixels
            avg /= block_size**2
            avg = round(avg)
            color = (
                (255 if avg == 1 else 0)
                if grayscale
                else (255, 255, 255) if avg == 1 else (0, 0, 0)
            )
            blocks[i // block_size, j // block_size] = (
                color == (255, 255, 255) if not grayscale else color == 255
            )

            # Color pixels depending on average
            for x in range(i, i + block_size):
                for y in range(j, j + block_size):
                    pixels[x, y] = color
    img.show()
    return blocks


def writeBlocksToFile(blocks, filename):
    with open(f"{filename}.pc", "w") as file:
        colLine = ""
        rowLine = ""

        for i in range(DIMENSIONS):
            row = blocks[i, :]
            col = blocks[:, i]

            lineNumber = 0
            colNumber = 0
            for j in range(DIMENSIONS):
                if row[j]:
                    lineNumber += 1
                elif lineNumber != 0:
                    colLine += f"{lineNumber} "
                    lineNumber = 0

                if col[j]:
                    colNumber += 1
                elif colNumber != 0:
                    rowLine += f"{colNumber} "
                    colNumber = 0

            if lineNumber != 0:
                colLine += f"{lineNumber} "
            if colNumber != 0:
                rowLine += f"{colNumber} "

            if i != DIMENSIONS - 1:
                colLine += "| "
                rowLine += "| "

        file.write(colLine + "\n")
        file.write(rowLine + "\n")


def writeSolution(blocks, filename):
    with open(f"{filename}.pcs", "w") as file:
        for i in range(DIMENSIONS):
            for j in range(DIMENSIONS):
                file.write("#" if blocks[j, i] else ".")
            file.write("\n")


if __name__ == "__main__":
    main()
