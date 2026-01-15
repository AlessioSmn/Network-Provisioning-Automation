#!/bin/bash

# Default values
BRIDGE=NO
CLEAN=NO
TEMPLATE=NO
IMAGES=NO
SSHCERT=NO

print_help() {
  cat <<EOF
Usage: $0 [OPTIONS]

Options (no arguments required):
  -i, --images      Build images (default: NO)
  -c, --clean       Clean previous launch (default: NO)
  -b, --bridge      Create bridges (default: NO)
  -t, --template    Compile templates (default: NO)
  -s, --sshclean    Clean SSH certificates of nodes (default: NO)
  -h, --help        Show this help message and exit
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -b|--bridge) BRIDGE=YES ;;
    -c|--clean) CLEAN=YES ;;
    -t|--template) TEMPLATE=YES ;;
    -i|--images) IMAGES=YES ;;
    -s|--sshclean) SSHCERT=YES ;;
    -h|--help) print_help; exit 0 ;;
    --) shift; break ;;
    *) echo "Unknown option: $1"; print_help; exit 1 ;;
  esac
  shift
done

# Build images
if [[ "$IMAGES" == "YES" ]]; then
    echo -e "\n========= Build images ========="
    ./shell/images.sh
fi

# Clear ssh certificates
if [[ "$SSHCERT" == "YES" ]]; then
    echo -e "\n========= Clear SSH certificates ========="
    ./shell/sshcert.sh
fi

# Clear previous lab
if [[ "$CLEAN" == "YES" ]]; then
    echo -e "\n========= Clear CLAB ========="
    ./shell/clean.sh
fi

# Create bridges
if [[ "$BRIDGE" == "YES" ]]; then
    echo -e "\n========= Setup bridges ========="
    ./shell/bridge.sh
fi

# Compile templates
if [[ "$TEMPLATE" == "YES" ]]; then
    echo -e "\n========= Templates ========="
    ./shell/template.sh
fi

# Startup
echo -e "\n========= CLAB Deploy ========="
sudo containerlab deploy -t acn.clab.yml