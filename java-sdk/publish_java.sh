#!/bin/bash

# AIGC Compliance Java SDK - Publication Script
# This script builds and publishes the Java SDK to Maven Central

set -e  # Exit on any error

echo "🚀 AIGC Compliance Java SDK Publication Script"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
GROUP_ID="com.aigc-compliance"
ARTIFACT_ID="java-sdk"
TARGET_DIR="target"

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
if [[ ! -f "pom.xml" ]]; then
    print_error "pom.xml not found. Please run this script from the java-sdk directory."
    exit 1
fi

# Check if required tools are installed
print_step "Checking required tools..."

if ! command -v java &> /dev/null; then
    print_error "Java is required but not installed."
    exit 1
fi

if ! command -v mvn &> /dev/null; then
    print_error "Maven is required but not installed."
    exit 1
fi

# Check Java version (minimum 8)
JAVA_VERSION=$(java -version 2>&1 | head -n1 | cut -d'"' -f2 | cut -d'.' -f1-2)
if [[ "$JAVA_VERSION" < "1.8" ]] && [[ "$JAVA_VERSION" < "8" ]]; then
    print_error "Java 8+ is required. Current version: $(java -version 2>&1 | head -n1)"
    exit 1
fi

print_success "All required tools are available. Java $(java -version 2>&1 | head -n1 | cut -d'"' -f2), Maven $(mvn --version | head -n1 | cut -d' ' -f3)"

# Check Maven settings for deployment
print_step "Checking Maven configuration..."
if [[ ! -f "$HOME/.m2/settings.xml" ]]; then
    print_warning "Maven settings.xml not found. You'll need to configure it for OSSRH deployment."
    echo ""
    echo "📝 Create ~/.m2/settings.xml with your OSSRH credentials:"
    echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
    echo "<settings>"
    echo "  <servers>"
    echo "    <server>"
    echo "      <id>ossrh</id>"
    echo "      <username>your-jira-username</username>"
    echo "      <password>your-jira-password</password>"
    echo "    </server>"
    echo "  </servers>"
    echo "</settings>"
    echo ""
fi

# Clean previous builds
print_step "Cleaning previous builds..."
mvn clean
print_success "Previous builds cleaned."

# Compile and run tests
print_step "Compiling and running tests..."
mvn compile test
print_success "Compilation and tests completed."

# Run code quality checks
print_step "Running code quality checks..."
if mvn checkstyle:check &> /dev/null; then
    print_success "Code style check passed."
else
    print_warning "Code style issues found. Please review checkstyle report."
fi

# Package the application
print_step "Packaging application..."
mvn package
print_success "Application packaged successfully."

# List built files
print_step "Built files:"
ls -la $TARGET_DIR/

# Check current version
CURRENT_VERSION=$(mvn help:evaluate -Dexpression=project.version -q -DforceStdout)
echo ""
echo "📦 Java SDK is ready for publication!"
echo "Current version: $CURRENT_VERSION"
echo ""

# Check if it's a SNAPSHOT version
if [[ "$CURRENT_VERSION" == *"SNAPSHOT"* ]]; then
    print_warning "This is a SNAPSHOT version. Consider releasing a stable version for production."
    echo ""
    read -p "Do you want to release a stable version? [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_step "Preparing release version..."
        mvn versions:set -DremoveSnapshot
        NEW_VERSION=$(mvn help:evaluate -Dexpression=project.version -q -DforceStdout)
        print_success "Version updated to: $NEW_VERSION"
        
        # Rebuild with new version
        mvn clean package
    fi
fi

# GPG signing check
print_step "Checking GPG configuration..."
if command -v gpg &> /dev/null; then
    if gpg --list-secret-keys | grep -q "sec"; then
        print_success "GPG keys found for signing."
    else
        print_warning "No GPG secret keys found. You'll need to set up GPG signing for Maven Central."
        echo ""
        echo "🔑 GPG Setup instructions:"
        echo "1. Generate a key: gpg --gen-key"
        echo "2. List keys: gpg --list-keys"
        echo "3. Upload to keyserver: gpg --keyserver keyserver.ubuntu.com --send-keys YOUR_KEY_ID"
    fi
else
    print_error "GPG is required for Maven Central deployment but not found."
    exit 1
fi

# Deployment options
echo ""
echo "📋 Deployment Options:"
echo "======================"
echo "1) Deploy to OSSRH Snapshots (testing)"
echo "2) Deploy to OSSRH Staging (pre-release)"
echo "3) Release to Maven Central (production)"
echo "4) Install locally only"
echo ""

read -p "Choose deployment option [1-4]: " -n 1 -r DEPLOY_CHOICE
echo ""

case $DEPLOY_CHOICE in
    1)
        print_step "Deploying to OSSRH Snapshots..."
        mvn clean deploy
        print_success "Deployed to OSSRH Snapshots successfully!"
        echo ""
        echo "🧪 Snapshot available at:"
        echo "   https://s01.oss.sonatype.org/content/repositories/snapshots/"
        ;;
    2)
        print_step "Deploying to OSSRH Staging..."
        mvn clean deploy -P release
        print_success "Deployed to OSSRH Staging successfully!"
        echo ""
        echo "📋 Next steps for staging:"
        echo "1. Log into https://s01.oss.sonatype.org/"
        echo "2. Go to Staging Repositories"
        echo "3. Find your repository and close it"
        echo "4. If validation passes, release it to Maven Central"
        ;;
    3)
        print_step "Releasing to Maven Central..."
        echo "⚠️  This will publish to Maven Central and cannot be undone!"
        read -p "Are you absolutely sure? [y/N]: " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            mvn clean deploy -P release
            print_success "Released to Maven Central successfully!"
            echo ""
            echo "🎉 PUBLICATION COMPLETE!"
            echo "======================================"
            echo "Your artifact will be available at:"
            echo "   https://search.maven.org/artifact/$GROUP_ID/$ARTIFACT_ID"
            echo ""
            echo "Users can now include in their pom.xml:"
            echo "<dependency>"
            echo "  <groupId>$GROUP_ID</groupId>"
            echo "  <artifactId>$ARTIFACT_ID</artifactId>"
            echo "  <version>$(mvn help:evaluate -Dexpression=project.version -q -DforceStdout)</version>"
            echo "</dependency>"
        else
            print_warning "Release to Maven Central cancelled."
        fi
        ;;
    4)
        print_step "Installing locally..."
        mvn install
        print_success "Installed to local Maven repository successfully!"
        echo ""
        echo "📦 Local installation complete!"
        echo "Available in your local ~/.m2/repository/"
        ;;
    *)
        print_error "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
print_step "Cleaning up..."
read -p "Clean target directory? [Y/n]: " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    mvn clean
    print_success "Target directory cleaned."
fi

echo ""
print_success "Script completed!"

# Display next steps
echo ""
echo "📋 Next Steps:"
echo "==============="
echo "1. Verify artifact accessibility"
echo "2. Update documentation with Maven coordinates"
echo "3. Create GitHub release with changelog"
echo "4. Update sample projects and examples"
echo "5. Monitor Maven Central sync (can take 2+ hours)"
echo ""

# Git tag suggestion
if [[ "$CURRENT_VERSION" != *"SNAPSHOT"* ]]; then
    echo "💡 Suggested Git commands:"
    echo "   git add pom.xml"
    echo "   git commit -m \"Release v$CURRENT_VERSION\""
    echo "   git tag v$CURRENT_VERSION"
    echo "   git push origin main --tags"
    echo ""
fi

exit 0