import argparse
import psd_to_usd.convert as convert
import logging

parser = argparse.ArgumentParser(description='Convert PSD to USD')
parser.add_argument('input', type=str, help='Path to PSD input file')
parser.add_argument('output', type=str, help='Path for USD output file')

# parser.add_argument('working_dir', type=str, help='Path for ' default=None)

args = parser.parse_args()

_input = args.input
_output = args.output

# logging.basicConfig(format='%(levelname)s:\t%(message)s', level=logging.DEBUG)
# logging.info("Converting PSD to USD")
# logging.info(f" - input: {_input}")
# logging.info(f" - output: {_output}")

convert.convert(_input, _output)
