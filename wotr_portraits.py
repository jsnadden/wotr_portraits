import os
import sys
import argparse
from pathlib import Path
from PIL import Image
import json
from PySide6.QtWidgets import QApplication, QMainWindow

######################################################################################################
# PARSE COMMAND-LINE ARGUMENTS

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument(dest='image', help="Filepath of character image.", type=str)
arg_parser.add_argument(dest='charname', help="Name of character.", type=str)
arg_parser.add_argument('-p', '--portraits', dest='portraits', help="Directory where game looks for custom portraits, by default: %APPDATA%\\LocalLow\\Owlcat Games\\Pathfinder Wrath Of The Righteous\\Portraits", type=str)
args = arg_parser.parse_args()

# validate character image exists
input_image_path = Path(args.image)
if not input_image_path.is_file():
	print("Specified file not found: " + str(input_image_path) , file=sys.stderr)
	sys.exit(2)

# validate custom portrait directory exists
local_low_path = Path(os.environ["LOCALAPPDATA"]).parent / "LocalLow"
portraits_path = Path(args.portraits) if args.portraits is not None else local_low_path / "Owlcat Games" / "Pathfinder Wrath Of The Righteous" / "Portraits"
output_dir_path = portraits_path / args.charname
if not portraits_path.is_dir():
	print("Portraits directory not found: " + str(portraits_path) , file=sys.stderr)
	sys.exit(2)

######################################################################################################
# LOAD CHARACTER IMAGE

# attempt to load image
original_image: (Image.Image | None) = None
try:
	with Image.open(input_image_path, 'r') as image_file:
		original_image = image_file.copy()

except ValueError as e:
	print(f"Failed to load image: {e}")
	sys.exit(1)
except PermissionError:
	print("You do not have the required permissions to access this file.", file=sys.stderr)
	sys.exit(1)
except OSError as e:
	print(f"System/IO Error occurred: {e}", file=sys.stderr)
	sys.exit(1)

######################################################################################################
# INITIALISE/DESERIALISE CROP DATA

# default crop sizes
crop_keys = ["full", "medium", "small"]
crop_data = {crop_keys[i] : (0.0, 0.0, 1.0/(i+1), 1.0/(i+1)) for i in range(3)}

json_path = output_dir_path / "crops.json"
if json_path.is_file():
	json_data = {}

	#attempt to load json file
	try:
		with open(json_path, 'r') as json_file:
			json_data = json.load(json_file)

	except json.JSONDecodeError as e:
		print(f"Invalid JSON: {e}")
		sys.exit(1)
	except PermissionError:
		print("You do not have the required permissions to access this file.", file=sys.stderr)
		sys.exit(1)
	except OSError as e:
		print(f"System/IO Error occurred: {e}", file=sys.stderr)
		sys.exit(1)

	# validate json data is as expected
	if isinstance(json_data, dict) and len(json_data) == 3 and set(json_data) == set(crop_keys) and all(
		isinstance(key, str)
		and isinstance(value, list)
		and len(value) == 4
		and all(type(i) is float for i in value)
		for key,value in json_data.items()
	):
		crop_data = {key : tuple(value) for key,value in json_data.items()}

######################################################################################################
# BEGIN QT APPLICATION

app = QApplication([])

# setup window
window = QMainWindow()
window.setWindowTitle("Pathfinder: WotR Custom Portrait Tool")
screen = app.primaryScreen()
available_geometry = screen.availableGeometry()
window_width = int(min(.5 * available_geometry.width(), 1920))
window_height = int(min(.6667 * available_geometry.height(), 1080))
window.resize(window_width, window_height)
window.show()

sys.exit(app.exec())

# TODO: reorganise so that qt is the WHOLE application, not just this step





######################################################################################################
# OUTPUT PORTRAIT IMAGES AND JSON CROP DATA

# ensure output directory exists
#output_dir_path.mkdir(parents=False, exist_ok=True)

# USING crop_data, CREATE/EDIT OUTPUT IMAGES AND SAVE TO DISC (HANDLING FILE IO ERRORS)
#output_file_paths = {
#		"full" : output_dir_path / "Fulllength.png",
#		"medium" : output_dir_path / "Medium.png",
#		"small" : output_dir_path / "Small.png"
#	}

# SAVE crop_data TO JSON FILE (OVERWRITING, HANDLING FILE IO ERRORS)
