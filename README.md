# KiCAD QR Code Generator for CI use

A Python script designed to automate the process of adding information to KiCAD PCBs by generating a QR code with the specified data and placing it at a designated location. This tool is particularly useful for adding versioning or other metadata to PCBs in a Continuous Integration (CI) pipeline.

## Features

- **Automated QR Code Generation**: Generates QR codes with version information or any data.
- **Flexible Placement**: Automatically places the QR code at a specified text location on the PCB.
- **Auto-sizes QR**: Automatically selects the correct QR resolution based on data.
- **Supports KiCAD Files**: Works directly with KiCAD PCB files (`.kicad_pcb`).
- **CI/CD Friendly**: Designed for use in automated environments, making it easy to integrate with CI pipelines.
- **Proper return-codes**: Exits with error if the placeholder cannot be found, for use in CI to detect if it's missing.

## Requirements

- Python 3.6 or higher
- KiCAD v8 (for the `pcbnew` Python module)
- [Pillow](https://python-pillow.org/) (PIL) for image manipulation
- [qrcode](https://pypi.org/project/qrcode/) library for generating QR codes

## Installation

1. Install Python dependencies:

    ```bash
    pip install Pillow qrcode
    ```

2. Make sure KiCAD is installed and properly configured to use its Python scripting capabilities.

## Usage

In KiCAD, add a textbox that has the text you want to use as identifier in the command. The textbox should be square, however the script will make the best effort if it is not.

Then run the script with the required arguments:

```bash
> python kicad_qr_inserter.py --help

usage: kicad_qr_inserter.py [-h] [-o OUTPUT_FILE] -t TEXTBOX_IDENTIFIER -d DATA [-q]
                            input_file

Generate a QR code and place it on a KiCAD v8 PCB.

positional arguments:
  input_file            Path to the input KiCAD PCB file.

options:
  -h, --help            show this help message and exit
  -o OUTPUT_FILE, --output_file OUTPUT_FILE
                        Path to the output KiCAD PCB file. If not provided, overwrites the
                        input file.
  -t TEXTBOX_IDENTIFIER, --textbox_identifier TEXTBOX_IDENTIFIER
                        Textbox identifier to find on the PCB.
  -d DATA, --data DATA  Data to encode in the QR code.
  -q, --quiet           Suppress output messages.
```

## Example

The `test.kicad_pcb` file before running the script:

![Before running script](pre.png)


After running `python kicad_qr_inserter.py -t QR_MARKER -d "0123abc,v12.12" -q test.kicad_pcb`:

![After running script](post.png)


