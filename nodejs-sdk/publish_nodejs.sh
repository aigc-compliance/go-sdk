#!/bin/bash

# AIGC Compliance Node.js SDK - Publication Script
# This script builds and publishes the Node.js SDK to npm

set -e  # Exit on any error

echo "🚀 AIGC Compliance Node.js SDK Publication Script"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PACKAGE_NAME="@aigc-compliance/sdk"
DIST_DIR="dist"
COVERAGE_DIR="coverage"

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
if [[ ! -f "package.json" ]]; then
    print_error "package.json not found. Please run this script from the nodejs-sdk directory."
    exit 1
fi

# Check if required tools are installed
print_step "Checking required tools..."

if ! command -v node &> /dev/null; then
    print_error "Node.js is required but not installed."
    exit 1
fi

if ! command -v npm &> /dev/null; then
    print_error "npm is required but not installed."
    exit 1
fi

# Check Node.js version (minimum 14)
NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 14 ]; then
    print_error "Node.js 14+ is required. Current version: $(node --version)"
    exit 1
fi

print_success "All required tools are available. Node.js $(node --version), npm $(npm --version)"

# Check if user is logged in to npm
if ! npm whoami &> /dev/null; then
    print_error "You are not logged in to npm. Please run: npm login"
    exit 1
fi

print_success "Logged in to npm as: $(npm whoami)"

# Install dependencies
print_step "Installing dependencies..."
npm ci
print_success "Dependencies installed."

# Clean previous builds
print_step "Cleaning previous builds..."
npm run clean 2>/dev/null || rm -rf $DIST_DIR $COVERAGE_DIR
print_success "Cleaned build directories."

# Run linting
print_step "Running linter..."
if npm run lint &> /dev/null; then
    print_success "Linting passed."
else
    print_warning "Linting issues found. Running auto-fix..."
    npm run lint:fix || print_warning "Some linting issues could not be auto-fixed."
fi

# Run formatting
print_step "Running code formatting..."
npm run format
print_success "Code formatted."

# Build the package
print_step "Building TypeScript..."
npm run build
print_success "TypeScript compiled successfully."

# Run tests
print_step "Running tests..."
if npm test; then
    print_success "All tests passed."
else
    print_error "Tests failed. Please fix failing tests before publishing."
    exit 1
fi

# Run test coverage
print_step "Running test coverage..."
npm run test:coverage
print_success "Test coverage completed."

# Check package integrity
print_step "Checking package integrity..."
npm pack --dry-run
print_success "Package integrity check passed."

# List built files
print_step "Built files:"
ls -la $DIST_DIR/

# Prompt for version bump
echo ""
echo "📦 Package is ready for publication!"
echo ""

# Check current version
CURRENT_VERSION=$(node -p "require('./package.json').version")
echo "Current version: $CURRENT_VERSION"
echo ""

# Version bump options
echo "Version bump options:"
echo "1) patch (x.x.X) - Bug fixes"
echo "2) minor (x.X.x) - New features"
echo "3) major (X.x.x) - Breaking changes"
echo "4) Skip version bump"
echo ""

read -p "Choose version bump [1-4]: " -n 1 -r VERSION_CHOICE
echo ""

case $VERSION_CHOICE in
    1)
        print_step "Bumping patch version..."
        npm version patch --no-git-tag-version
        ;;
    2)
        print_step "Bumping minor version..."
        npm version minor --no-git-tag-version
        ;;
    3)
        print_step "Bumping major version..."
        npm version major --no-git-tag-version
        ;;
    4)
        print_warning "Skipping version bump."
        ;;
    *)
        print_error "Invalid choice. Exiting."
        exit 1
        ;;
esac

NEW_VERSION=$(node -p "require('./package.json').version")
if [ "$NEW_VERSION" != "$CURRENT_VERSION" ]; then
    print_success "Version updated to: $NEW_VERSION"
fi

# Check if we should publish to npm test registry first
echo ""
read -p "Do you want to publish to npm (Test) first? (recommended) [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_step "Publishing to npm with --dry-run flag..."
    npm publish --dry-run --access public
    print_success "Dry run completed successfully!"
    
    echo ""
    read -p "Dry run successful. Ready to publish to npm? [y/N]: " -n 1 -r
    echo
fi

# Publish to npm
if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
    read -p "Publish to npm? This action cannot be undone! [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_step "Publishing to npm..."
        npm publish --access public
        print_success "Published to npm successfully!"
        
        echo ""
        echo "🎉 PUBLICATION COMPLETE!"
        echo "======================================"
        echo "Your package is now available at:"
        echo "   https://www.npmjs.com/package/$PACKAGE_NAME"
        echo ""
        echo "Users can now install with:"
        echo "   npm install $PACKAGE_NAME"
        echo ""
        echo "📚 Don't forget to:"
        echo "   - Update the documentation"
        echo "   - Create a release on GitHub"
        echo "   - Update changelog"
        echo "   - Announce the release"
        
        # Show package stats
        if command -v npx &> /dev/null; then
            echo ""
            print_step "Package information:"
            npx npm-stat $PACKAGE_NAME || echo "Install npm-stat to see download statistics: npm install -g npm-stat"
        fi
    else
        print_warning "Publication to npm cancelled."
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
    npm run clean
    print_success "Build files cleaned."
fi

echo ""
print_success "Script completed!"

# Display next steps
echo ""
echo "📋 Next Steps:"
echo "==============="
echo "1. Verify installation: npm install $PACKAGE_NAME"
echo "2. Test the installed package in a new project"
echo "3. Update documentation website"
echo "4. Create GitHub release with changelog"
echo "5. Update TypeScript definitions if needed"
echo "6. Monitor npm download statistics"
echo ""

# Git tag suggestion
if [ "$NEW_VERSION" != "$CURRENT_VERSION" ]; then
    echo "💡 Suggested Git commands:"
    echo "   git add package.json"
    echo "   git commit -m \"Release v$NEW_VERSION\""
    echo "   git tag v$NEW_VERSION"
    echo "   git push origin main --tags"
    echo ""
fi

exit 0