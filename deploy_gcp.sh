#!/bin/bash

# Google Cloud Platform Deployment Script
# This script deploys the rental platform search system to Google Cloud App Engine

set -e  # Exit on any error

echo "🚀 Google Cloud Platform Deployment"
echo "===================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    print_error "Google Cloud CLI (gcloud) is not installed!"
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

print_status "Google Cloud CLI found"

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    print_warning "Not authenticated with Google Cloud"
    echo "Please run: gcloud auth login"
    exit 1
fi

print_status "Google Cloud authentication verified"

# Set project
PROJECT_ID="data-417505"
print_info "Setting project to: $PROJECT_ID"
gcloud config set project $PROJECT_ID

# Enable required APIs
print_info "Enabling required Google Cloud APIs..."
gcloud services enable appengine.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable cloudbuild.googleapis.com

print_status "APIs enabled"

# Create App Engine application if it doesn't exist
print_info "Checking App Engine application..."
if ! gcloud app describe &> /dev/null; then
    print_info "Creating App Engine application..."
    gcloud app create --region=us-central
    print_status "App Engine application created"
else
    print_status "App Engine application already exists"
fi

# Clean up unwanted files before deployment
print_info "Cleaning up files for deployment..."
rm -rf __pycache__/
rm -rf */__pycache__/
rm -rf */*/__pycache__/
find . -name "*.pyc" -delete
find . -name "*.pyo" -delete
rm -f *.log
rm -f *.tmp
rm -f *.temp
rm -f *.bak
rm -f *.backup

# Remove development files
rm -rf myenv/
rm -rf .git/
rm -rf tests/
rm -rf production/
rm -f .env
rm -f .env.local
rm -f .env.development
rm -f .gitignore
rm -f README.md
rm -f DEPLOYMENT_GUIDE.md
rm -f setup_production.sh
rm -f Makefile
rm -f pytest.ini
rm -f LICENSE
rm -f API_EXAMPLES.md
rm -f ELASTICSEARCH_FIX.md

print_status "Files cleaned up"

# Deploy to App Engine
print_info "Deploying to Google Cloud App Engine..."
echo "This may take a few minutes..."

gcloud app deploy app.yaml --quiet

print_status "Deployment completed!"

# Get the deployed URL
APP_URL=$(gcloud app browse --no-launch-browser)
print_status "Application deployed successfully!"
echo ""
echo "🌐 Your application is available at:"
echo "   $APP_URL"
echo ""
echo "📊 Available endpoints:"
echo "   • Health Check: $APP_URL/health"
echo "   • API Documentation: $APP_URL/docs"
echo "   • Search API: $APP_URL/api/v1/search"
echo "   • Properties: $APP_URL/api/v1/properties"
echo "   • Statistics: $APP_URL/api/v1/stats"
echo ""
echo "🔧 Google Cloud Console:"
echo "   • App Engine: https://console.cloud.google.com/appengine"
echo "   • Project: https://console.cloud.google.com/home/dashboard?project=$PROJECT_ID"
echo ""
print_warning "Next steps:"
echo "1. Test the health endpoint: $APP_URL/health"
echo "2. Generate embeddings: POST $APP_URL/api/v1/generate-embeddings"
echo "3. Test search: POST $APP_URL/api/v1/search"
echo "4. Monitor in Google Cloud Console"
echo ""
print_status "Deployment completed successfully! 🎉"
