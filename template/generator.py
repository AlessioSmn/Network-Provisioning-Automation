import sys
import os
import yaml
import jinja2
from jinja2 import Environment, FileSystemLoader

DBG_PRINT_TEMPLATE = False
DBG_PRINT_DATA = False
DBG_PRINT_CONTENT = True

print("Syntax:")
print("[python.exe | python3] [renderer.py] [template.j2] [data.yaml]")
print("WIN: \tpython.exe .\\renderer.py startup_config_template.j2 [.yaml]")
# python.exe .\renderer.py startup_config_template.j2 .\info_ceos2.yaml
# python.exe .\renderer.py startup_config_template.j2 .\info_ceos1.yaml

# ========= Get arguments
if len(sys.argv) != 3:
    print("Error: must specify <template> <data> as arguments")
    sys.exit(1)
    
# Template should be first argument
temp_filename = sys.argv[1]
if not os.path.isfile(temp_filename):
    print(f"Error: '{temp_filename}' is not a valid file")
    sys.exit(1)

# Data should be second argument
data_filename = sys.argv[2]
if not os.path.isfile(data_filename):
    print(f"Error: '{data_filename}' is not a valid file")
    sys.exit(1)


# ========= Load template and data
# Load template
environment = Environment(loader=FileSystemLoader("./"))
template = environment.get_template(temp_filename)

# Load data
with open(data_filename) as file:
    data = yaml.safe_load(file)

# Print for debug
if DBG_PRINT_TEMPLATE:
    print(template)
if DBG_PRINT_DATA:
    print(data)


# ========= Generate content
content = template.render(data)


# ========= Print and save to file

if DBG_PRINT_CONTENT:
    print(content)

content_filename = data['config_filename']

with open(content_filename, "w", newline="") as f:
    f.write(content)
print(f"Content saved to {content_filename}")
