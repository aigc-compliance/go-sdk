#!/bin/bash

# AIGC Compliance Go SDK - Publication Script
# This script builds and publishes the Go SDK to Go Modules

set -e  # Exit on any error

echo "🚀 AIGC Compliance Go SDK Publication Script"
echo "============================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
MODULE_NAME="github.com/aigc-compliance/go-sdk"

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
if [[ ! -f "go.mod" ]]; then
    print_error "go.mod not found. Please run this script from the go-sdk directory."
    exit 1
fi

# Check if required tools are installed
print_step "Checking required tools..."

if ! command -v go &> /dev/null; then
    print_error "Go is required but not installed."
    exit 1
fi

if ! command -v git &> /dev/null; then
    print_error "Git is required but not installed."
    exit 1
fi

# Check Go version (minimum 1.18)
GO_VERSION=$(go version | cut -d' ' -f3 | sed 's/go//')
MIN_VERSION="1.18"
if [[ "$(printf '%s\n' "$MIN_VERSION" "$GO_VERSION" | sort -V | head -n1)" != "$MIN_VERSION" ]]; then
    print_error "Go $MIN_VERSION+ is required. Current version: $GO_VERSION"
    exit 1
fi

print_success "All required tools are available. Go $GO_VERSION, Git $(git --version | cut -d' ' -f3)"

# Verify we're in a Git repository
if [[ ! -d ".git" ]]; then
    print_error "Not in a Git repository. Go modules require Git for versioning."
    exit 1
fi

# Check if remote origin exists
if ! git remote get-url origin &> /dev/null; then
    print_error "No Git remote 'origin' found. Please set up the GitHub repository first."
    exit 1
fi

REPO_URL=$(git remote get-url origin)
print_success "Git repository: $REPO_URL"

# Clean mod cache and verify dependencies
print_step "Cleaning and verifying Go modules..."
go clean -modcache
go mod tidy
go mod verify
print_success "Go modules verified."

# Run go fmt
print_step "Formatting Go code..."
go fmt ./...
print_success "Code formatted."

# Run go vet
print_step "Running go vet..."
go vet ./...
print_success "go vet passed."

# Run tests
print_step "Running tests..."
if go test ./... -v; then
    print_success "All tests passed."
else
    print_error "Tests failed. Please fix failing tests before publishing."
    exit 1
fi

# Run tests with race detection
print_step "Running tests with race detection..."
if go test ./... -race; then
    print_success "Race condition tests passed."
else
    print_warning "Race condition tests failed. Consider fixing before publishing."
fi

# Run benchmarks (if any)
print_step "Running benchmarks..."
if go test ./... -bench=. -benchtime=1s &> /dev/null; then
    print_success "Benchmarks completed."
else
    print_warning "No benchmarks found or benchmarks failed."
fi

# Build for multiple architectures to ensure compatibility
print_step "Testing cross-compilation..."
GOOS=linux GOARCH=amd64 go build ./...
GOOS=windows GOARCH=amd64 go build ./...
GOOS=darwin GOARCH=amd64 go build ./...
GOOS=darwin GOARCH=arm64 go build ./...
print_success "Cross-compilation successful for major platforms."

# Check for common issues
print_step "Running additional checks..."

# Check for potential security issues with govulncheck (if available)
if command -v govulncheck &> /dev/null; then
    if govulncheck ./...; then
        print_success "No known security vulnerabilities found."
    else
        print_warning "Security vulnerabilities detected. Please review."
    fi
else
    print_warning "govulncheck not found. Install with: go install golang.org/x/vuln/cmd/govulncheck@latest"
fi

# Check for potential issues with staticcheck (if available)
if command -v staticcheck &> /dev/null; then
    if staticcheck ./...; then
        print_success "Staticcheck passed."
    else
        print_warning "Staticcheck found issues. Please review."
    fi
else
    print_warning "staticcheck not found. Install with: go install honnef.co/go/tools/cmd/staticcheck@latest"
fi

# Check current version/tag
print_step "Checking version information..."
CURRENT_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "no-tags")
echo "Current tag: $CURRENT_TAG"

# Check if there are uncommitted changes
if [[ -n $(git status --porcelain) ]]; then
    print_warning "You have uncommitted changes:"
    git status --short
    echo ""
    read -p "Do you want to commit these changes? [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter commit message: " COMMIT_MSG
        git add .
        git commit -m "$COMMIT_MSG"
        print_success "Changes committed."
    else
        print_warning "Proceeding with uncommitted changes."
    fi
fi

# Check if we're on main/master branch
CURRENT_BRANCH=$(git branch --show-current)
if [[ "$CURRENT_BRANCH" != "main" && "$CURRENT_BRANCH" != "master" ]]; then
    print_warning "You're not on main/master branch. Current branch: $CURRENT_BRANCH"
    read -p "Continue anyway? [y/N]: " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "Aborting. Please switch to main/master branch."
        exit 1
    fi
fi

echo ""
echo "📦 Go SDK is ready for publication!"
echo ""

# Version options
echo "🏷️  VERSION OPTIONS"
echo "==================="
echo "1) Create patch version (v1.0.X)"
echo "2) Create minor version (v1.X.0)"  
echo "3) Create major version (vX.0.0)"
echo "4) Create custom version"
echo "5) Skip versioning (publish current state)"
echo ""

read -p "Choose version option [1-5]: " -n 1 -r VERSION_CHOICE
echo ""

case $VERSION_CHOICE in
    1)
        if [[ "$CURRENT_TAG" == "no-tags" ]]; then
            NEW_VERSION="v1.0.1"
        else
            # Extract version and increment patch
            BASE_VERSION=$(echo "$CURRENT_TAG" | sed 's/v//' | cut -d'.' -f1,2)
            PATCH_VERSION=$(echo "$CURRENT_TAG" | sed 's/v//' | cut -d'.' -f3)
            NEW_PATCH=$((PATCH_VERSION + 1))
            NEW_VERSION="v${BASE_VERSION}.${NEW_PATCH}"
        fi
        ;;
    2)
        if [[ "$CURRENT_TAG" == "no-tags" ]]; then
            NEW_VERSION="v1.1.0"
        else
            MAJOR_VERSION=$(echo "$CURRENT_TAG" | sed 's/v//' | cut -d'.' -f1)
            MINOR_VERSION=$(echo "$CURRENT_TAG" | sed 's/v//' | cut -d'.' -f2)
            NEW_MINOR=$((MINOR_VERSION + 1))
            NEW_VERSION="v${MAJOR_VERSION}.${NEW_MINOR}.0"
        fi
        ;;
    3)
        if [[ "$CURRENT_TAG" == "no-tags" ]]; then
            NEW_VERSION="v2.0.0"
        else
            MAJOR_VERSION=$(echo "$CURRENT_TAG" | sed 's/v//' | cut -d'.' -f1)
            NEW_MAJOR=$((MAJOR_VERSION + 1))
            NEW_VERSION="v${NEW_MAJOR}.0.0"
        fi
        ;;
    4)
        read -p "Enter custom version (e.g., v1.0.0): " NEW_VERSION
        if [[ ! "$NEW_VERSION" =~ ^v[0-9]+\.[0-9]+\.[0-9]+.*$ ]]; then
            print_error "Invalid version format. Use semantic versioning (v1.0.0)."
            exit 1
        fi
        ;;
    5)
        print_warning "Skipping versioning. Publishing current state."
        NEW_VERSION=""
        ;;
    *)
        print_error "Invalid choice. Exiting."
        exit 1
        ;;
esac

# Create and push tag if version was chosen
if [[ -n "$NEW_VERSION" ]]; then
    print_step "Creating version tag: $NEW_VERSION"
    
    # Check if tag already exists
    if git tag -l | grep -q "^${NEW_VERSION}$"; then
        print_error "Tag $NEW_VERSION already exists."
        exit 1
    fi
    
    git tag -a "$NEW_VERSION" -m "Release $NEW_VERSION"
    print_success "Tag $NEW_VERSION created."
fi

# Push to GitHub
print_step "Pushing to GitHub..."
git push origin "$CURRENT_BRANCH"

if [[ -n "$NEW_VERSION" ]]; then
    git push origin "$NEW_VERSION"
    print_success "Tag $NEW_VERSION pushed to GitHub."
fi

print_success "Code pushed to GitHub successfully!"

# Go proxy instructions
echo ""
echo "🌐 GO MODULES PUBLICATION"
echo "========================="
echo ""
echo "✅ Your Go module is now published!"
echo ""
echo "📦 Module information:"
echo "   Module: $MODULE_NAME"
if [[ -n "$NEW_VERSION" ]]; then
    echo "   Version: $NEW_VERSION"
fi
echo "   Repository: $REPO_URL"
echo ""
echo "🔄 Go proxy sync:"
echo "The Go proxy (proxy.golang.org) will automatically discover your module"
echo "when someone first requests it. This usually happens within minutes."
echo ""
echo "Users can now import your module with:"
echo "   import \"$MODULE_NAME\""
echo ""
echo "And install it with:"
if [[ -n "$NEW_VERSION" ]]; then
    echo "   go get $MODULE_NAME@$NEW_VERSION"
else
    echo "   go get $MODULE_NAME"
fi
echo ""

# Trigger Go proxy fetch
if [[ -n "$NEW_VERSION" ]]; then
    print_step "Triggering Go proxy fetch..."
    PROXY_URL="https://proxy.golang.org/${MODULE_NAME}/@v/${NEW_VERSION}.info"
    if curl -s "$PROXY_URL" > /dev/null; then
        print_success "Go proxy successfully fetched the new version."
    else
        print_warning "Go proxy fetch failed. It may take a few minutes to become available."
    fi
fi

# Documentation links
echo ""
echo "📚 DOCUMENTATION & RESOURCES"
echo "============================"
echo "Your module documentation will be available at:"
echo "   https://pkg.go.dev/$MODULE_NAME"
if [[ -n "$NEW_VERSION" ]]; then
    echo "   https://pkg.go.dev/$MODULE_NAME@$NEW_VERSION"
fi
echo ""
echo "📊 Module information:"
echo "   https://goproxy.io/stats/$MODULE_NAME"
echo ""

print_success "Go SDK publication completed!"

# Display next steps
echo ""
echo "📋 Next Steps:"
echo "==============="
echo "1. Verify module accessibility: go get $MODULE_NAME"
echo "2. Check documentation at pkg.go.dev"
echo "3. Update README.md with installation instructions"
echo "4. Create GitHub release with changelog"
echo "5. Monitor download statistics"
echo "6. Update sample projects and examples"
echo ""

exit 0