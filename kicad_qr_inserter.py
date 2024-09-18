import pcbnew
import qrcode
from PIL import Image
import argparse

def find_text_location(board, text_identifier):
    """
    Finds the XY center location of a text identifier on a KiCAD PCB. Deletes the textbox on completion.
    
    :param board: Loaded KiCAD PCB file.
    :param text_identifier: The text content to search for.
    :return: A tuple (x center, y center, width, layer) with the location coordinates in mm, or None if not found.
    """
    
    # Iterate through all text items on the PCB
    for drawing in board.GetDrawings():
        if isinstance(drawing, pcbnew.PCB_TEXTBOX):
            if drawing.GetText() == text_identifier:
                pos = drawing.GetPosition()

                # Convert from internal units (nm) to mm
                x = pcbnew.ToMM(pos.x)
                y = pcbnew.ToMM(pos.y)
                end_x = pcbnew.ToMM(drawing.GetEndX())
                end_y = pcbnew.ToMM(drawing.GetEndY())

                layer = drawing.GetLayer()
                drawing.DeleteStructure()

                if end_x - x != end_y - y:
                    print("Warning! Textbox height != width")
                
                return (x + end_x) / 2, (y + end_y) / 2, (end_x - x + end_y - y) / 2, layer
    
    return None

def is_backside_layer(layer):
    """
    Checks if a given layer is a backside layer in KiCAD.

    :param layer: The layer to check (an integer or a layer constant from pcbnew).
    :return: True if the layer is on the backside, False otherwise.
    """
    backside_layers = [
        pcbnew.B_Cu,
        pcbnew.B_Adhes,
        pcbnew.B_Paste,
        pcbnew.B_SilkS,
        pcbnew.B_Mask,
        pcbnew.B_Fab,
        pcbnew.B_CrtYd,
    ]

    return layer in backside_layers

def generate_qr_code(data):
    """
    Generates a QR code image from the given data.
    
    :param data: The data to encode in the QR code.
    :return: PIL Image of the QR code.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=1,
        border=0
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill='black', back_color='white')
    return img

def insert_qr_to_pcb(qr_image, board, start_x, start_y, pixel_size, layer):
    """
    Converts a QR code image to a series of rectangles on a KiCAD PCB.
    
    :param qr_image: The QR code image (PIL Image).
    :param board: The KiCAD PCB object.
    :param start_x: X-coordinate for the top-left corner of the QR code.
    :param start_y: Y-coordinate for the top-left corner of the QR code.
    :param pixel_size: Size of each QR code pixel on the PCB.
    :param layer: The PCB layer to draw the QR code on.
    """
    width, height = qr_image.size

    if is_backside_layer(layer):
        qr_image = qr_image.transpose(Image.FLIP_LEFT_RIGHT)
        
    pixels = qr_image.load()

    for y in range(height):
        for x in range(width):
            if pixels[x, y] == 0:  # Black pixels are encoded as a square
                start_point = pcbnew.VECTOR2I(pcbnew.FromMM(start_x + x * pixel_size), pcbnew.FromMM(start_y + y * pixel_size))
                end_point = pcbnew.VECTOR2I(pcbnew.FromMM(start_x + (x + 1) * pixel_size), pcbnew.FromMM(start_y + (y + 1) * pixel_size))

                # Create a new shape (rectangle)
                rect_shape = pcbnew.PCB_SHAPE(board)
                rect_shape.SetShape(pcbnew.SHAPE_T_RECT)
                rect_shape.SetStart(start_point)
                rect_shape.SetEnd(end_point)
                rect_shape.SetLayer(layer)
                rect_shape.SetWidth(pcbnew.FromMM(0.0))
                rect_shape.SetFilled(True)

                board.Add(rect_shape)

def main():
    parser = argparse.ArgumentParser(description="Generate a QR code and place it on a KiCAD v8 PCB.")
    parser.add_argument('input_file', help="Path to the input KiCAD PCB file.")
    parser.add_argument('-o', '--output_file', help="Path to the output KiCAD PCB file. If not provided, overwrites the input file.", default=None)
    parser.add_argument('-t', '--textbox_identifier', help="Textbox identifier to find on the PCB.", required=True)
    parser.add_argument('-d', '--data', help="Data to encode in the QR code.", required=True)
    parser.add_argument('-q', '--quiet', action='store_true', help="Suppress output messages.")

    args = parser.parse_args()

    board = pcbnew.LoadBoard(args.input_file)

    location = find_text_location(board, args.textbox_identifier)

    if location:
        x, y, width, layer = location
        if not args.quiet:
            print(f"Found textbox '{args.textbox_identifier}' at location: X = {x:.2f} mm, Y = {y:.2f} mm, Size = {width:.2f} mm")
    
        qr_image = generate_qr_code(args.data)
        pixel_size = width / qr_image.width
        insert_qr_to_pcb(qr_image, board, x - qr_image.width / 2 * pixel_size, y - qr_image.width / 2 * pixel_size, pixel_size, layer)

        output_file_path = args.output_file if args.output_file else args.input_file
        pcbnew.SaveBoard(output_file_path, board)
        if not args.quiet:
            print(f"QR code added successfully and saved to '{output_file_path}'.")
        
    else:
        if not args.quiet:
            print(f"Textbox '{args.textbox_identifier}' not found on the PCB.")
        exit(1)

def main():
    parser = argparse.ArgumentParser(description="Generate a QR code and place it on a KiCAD PCB.")
    parser.add_argument('input_file', help="Path to the input KiCAD PCB file.")
    parser.add_argument('-o', '--output_file', help="Path to the output KiCAD PCB file. If not provided, overwrites the input file.", default=None)
    parser.add_argument('-t', '--text_identifier', help="Text identifier to find on the PCB.", required=True)
    parser.add_argument('-d', '--data', help="Data to encode in the QR code.", required=True)
    parser.add_argument('-q', '--quiet', action='store_true', help="Suppress output messages.")

    args = parser.parse_args()
    board = pcbnew.LoadBoard(args.input_file)

    replacement_count = 0
    while True:
        location = find_text_location(board, args.text_identifier)

        if location:
            x, y, width, layer = location
            
            if not args.quiet:
                print(f"Found textbox '{args.text_identifier}' at location: X = {x:.2f} mm, Y = {y:.2f} mm")
        
            qr_image = generate_qr_code(args.data)
            pixel_size = width / qr_image.width
            insert_qr_to_pcb(qr_image, board, x - qr_image.width / 2 * pixel_size, y - qr_image.width / 2 * pixel_size, pixel_size, layer)

            replacement_count += 1
        else:
            break  # No more matches found, exit the loop

    output_file_path = args.output_file if args.output_file else args.input_file
    pcbnew.SaveBoard(output_file_path, board)

    if not args.quiet:
        print(f"QR code added successfully. {replacement_count} replacements made. Saved to '{output_file_path}'.")
    
    if replacement_count == 0:
        if not args.quiet:
            print(f"No matches found for '{args.text_identifier}'.")
        sys.exit(1)


if __name__ == "__main__":
    main()
