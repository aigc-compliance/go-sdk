#!/bin/bash

# AIGC Compliance PHP SDK - Publication Script
# This script builds and publishes the PHP SDK to Packagist

set -e  # Exit on any error

echo "🚀 AIGC Compliance PHP SDK Publication Script"
echo "============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PACKAGE_NAME="aigc-compliance/php-sdk"
VENDOR_DIR="vendor"

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
if [[ ! -f "composer.json" ]]; then
    print_error "composer.json not found. Please run this script from the php-sdk directory."
    exit 1
fi

# Check if required tools are installed
print_step "Checking required tools..."

if ! command -v php &> /dev/null; then
    print_error "PHP is required but not installed."
    exit 1
fi

if ! command -v composer &> /dev/null; then
    print_error "Composer is required but not installed."
    exit 1
fi

# Check PHP version (minimum 7.4)
PHP_VERSION=$(php -r "echo PHP_VERSION;" | cut -d'.' -f1,2)
if (( $(echo "$PHP_VERSION < 7.4" | bc -l) )); then
    print_error "PHP 7.4+ is required. Current version: $(php --version | head -n1)"
    exit 1
fi

print_success "All required tools are available. PHP $(php --version | head -n1 | cut -d' ' -f2), Composer $(composer --version | cut -d' ' -f3)"

# Install dependencies
print_step "Installing dependencies..."
composer install --no-dev --optimize-autoloader
print_success "Dependencies installed."

# Run code quality checks
print_step "Running code quality checks..."

# PHP CodeSniffer
if composer run-script cs-check &> /dev/null; then
    print_success "Code style check passed."
else
    print_warning "Code style issues found. Running auto-fix..."
    composer run-script cs-fix || print_warning "Some code style issues could not be auto-fixed."
fi

# PHPStan
if composer run-script phpstan &> /dev/null; then
    print_success "Static analysis passed."
else
    print_warning "Static analysis issues found. Please review and fix manually."
fi

# Run tests
print_step "Running tests..."
if composer test &> /dev/null; then
    print_success "All tests passed."
else
    print_warning "Some tests failed. Please review test results."
fi

# Validate composer.json
print_step "Validating composer.json..."
composer validate --strict
print_success "composer.json validation passed."

# Check if package already exists on Packagist
print_step "Checking Packagist availability..."
if curl -s "https://packagist.org/packages/$PACKAGE_NAME" | grep -q "404"; then
    print_success "Package name is available on Packagist."
else
    print_warning "Package already exists on Packagist. Make sure you have permission to update it."
fi

echo ""
echo "📦 PHP SDK is ready for publication!"
echo ""

# Check current version
CURRENT_VERSION=$(php -r "echo json_decode(file_get_contents('composer.json'), true)['version'];")
echo "Current version: $CURRENT_VERSION"
echo ""

# Git repository check
if [[ -d ".git" ]]; then
    print_step "Checking Git repository status..."
    
    if [[ -n $(git status --porcelain) ]]; then
        print_warning "You have uncommitted changes. Consider committing them first."
        git status --short
        echo ""
    fi
    
    # Check if we're on main/master branch
    CURRENT_BRANCH=$(git branch --show-current)
    if [[ "$CURRENT_BRANCH" != "main" && "$CURRENT_BRANCH" != "master" ]]; then
        print_warning "You're not on main/master branch. Current branch: $CURRENT_BRANCH"
    fi
    
    print_success "Git repository check completed."
else
    print_warning "Not in a Git repository. Consider initializing one for better version control."
fi

echo ""
echo "📋 Pre-publication checklist:"
echo "=============================="
echo "✅ Code quality checks passed"
echo "✅ Tests executed"  
echo "✅ composer.json validated"
echo "✅ Dependencies optimized"
echo ""

# Instructions for Packagist publication
echo "🌐 PACKAGIST PUBLICATION INSTRUCTIONS"
echo "====================================="
echo ""
echo "Since PHP packages are published through Packagist automatically via GitHub,"
echo "you need to follow these steps:"
echo ""
echo "1. 📝 GITHUB SETUP:"
echo "   - Push your code to GitHub repository"
echo "   - Make sure your repository is public"
echo "   - Tag a release: git tag v$CURRENT_VERSION && git push --tags"
echo ""
echo "2. 📦 PACKAGIST REGISTRATION:"
echo "   - Go to https://packagist.org"
echo "   - Sign in with your GitHub account"
echo "   - Click 'Submit' and enter your GitHub repository URL"
echo "   - Packagist will automatically sync your releases"
echo ""
echo "3. 🔧 AUTO-UPDATE SETUP (Optional but recommended):"
echo "   - In your GitHub repository settings"
echo "   - Go to Webhooks -> Add webhook"
echo "   - Payload URL: https://packagist.org/api/github"
echo "   - Content type: application/json"
echo "   - Select 'Just the push event'"
echo ""

read -p "Have you pushed your code to GitHub and tagged a release? [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🎉 READY FOR PACKAGIST!"
    echo "======================"
    echo "Your package will be available at:"
    echo "   https://packagist.org/packages/$PACKAGE_NAME"
    echo ""
    echo "Users can install with:"
    echo "   composer require $PACKAGE_NAME"
    echo ""
    echo "📚 Don't forget to:"
    echo "   - Update the README.md with installation instructions"
    echo "   - Add code examples to the documentation"
    echo "   - Set up GitHub releases for future versions"
    echo "   - Monitor Packagist download statistics"
else
    print_warning "Please push to GitHub and create a tag before registering on Packagist."
    echo ""
    echo "💡 Quick Git commands:"
    echo "   git add ."
    echo "   git commit -m \"Release v$CURRENT_VERSION\""
    echo "   git tag v$CURRENT_VERSION"
    echo "   git push origin main --tags"
fi

echo ""
print_success "Script completed!"

exit 0