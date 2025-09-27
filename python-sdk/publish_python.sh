#!/bin/bash

# AIGC Compliance Python SDK - Publication Script
# This script builds and publishes the Python SDK to PyPI

set -e  # Exit on any error

echo "🚀 AIGC Compliance Python SDK Publication Script"
echo "================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PACKAGE_NAME="aigc-compliance"
DIST_DIR="dist"
BUILD_DIR="build"

# Function to print colored output
print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [[ ! -f "pyproject.toml" ]]; then
    print_error "pyproject.toml not found. Please run this script from the python-sdk directory."
    exit 1
fi

# Check if required tools are installed
print_step "Checking required tools..."

if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed."
    exit 1
fi

if ! python3 -c "import build" &> /dev/null; then
    print_warning "build package not found. Installing..."
    pip install build
fi

if ! python3 -c "import twine" &> /dev/null; then
    print_warning "twine package not found. Installing..."
    pip install twine
fi

print_success "All required tools are available."

# Clean previous builds
print_step "Cleaning previous builds..."
rm -rf $DIST_DIR $BUILD_DIR *.egg-info
print_success "Cleaned build directories."

# Run tests
print_step "Running tests..."
if command -v pytest &> /dev/null; then
    python3 -m pytest tests/ -v
    print_success "All tests passed."
else
    print_warning "pytest not found. Skipping tests. Install with: pip install pytest"
fi

# Build the package
print_step "Building package..."
python3 -m build
print_success "Package built successfully."

# List built files
print_step "Built files:"
ls -la $DIST_DIR/

# Check the package
print_step "Checking package integrity..."
python3 -m twine check $DIST_DIR/*
print_success "Package integrity check passed."

# Prompt for publication
echo ""
echo "📦 Package is ready for publication!"
echo "   Built files are in: $DIST_DIR/"
echo ""

# Check if we should publish to TestPyPI first
read -p "Do you want to publish to TestPyPI first? (recommended) [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_step "Publishing to TestPyPI..."
    python3 -m twine upload --repository testpypi $DIST_DIR/*
    print_success "Published to TestPyPI successfully!"
    
    echo ""
    echo "🧪 Test your package with:"
    echo "   pip install --index-url https://test.pypi.org/simple/ $PACKAGE_NAME"
    echo ""
    
    read -p "Test completed? Ready to publish to PyPI? [y/N]: " -n 1 -r
    echo
fi

# Publish to PyPI
if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
    read -p "Publish to PyPI? This action cannot be undone! [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_step "Publishing to PyPI..."
        python3 -m twine upload $DIST_DIR/*
        print_success "Published to PyPI successfully!"
        
        echo ""
        echo "🎉 PUBLICATION COMPLETE!"
        echo "======================================"
        echo "Your package is now available at:"
        echo "   https://pypi.org/project/$PACKAGE_NAME/"
        echo ""
        echo "Users can now install with:"
        echo "   pip install $PACKAGE_NAME"
        echo ""
        echo "📚 Don't forget to:"
        echo "   - Update the documentation"
        echo "   - Create a release on GitHub"
        echo "   - Announce the release"
    else
        print_warning "Publication to PyPI cancelled."
    fi
else
    print_warning "Publication cancelled."
fi

echo ""
print_step "Cleaning up..."
# Optionally clean build files
read -p "Clean build files? [Y/n]: " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    rm -rf $DIST_DIR $BUILD_DIR *.egg-info
    print_success "Build files cleaned."
fi

echo ""
print_success "Script completed!"

# Display next steps
echo ""
echo "📋 Next Steps:"
echo "==============="
echo "1. Verify installation: pip install $PACKAGE_NAME"
echo "2. Test the installed package"
echo "3. Update documentation website"
echo "4. Create GitHub release with changelog"
echo "5. Announce on social media/blog"
echo "6. Monitor PyPI download statistics"
echo ""

exit 0