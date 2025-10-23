#!/bin/bash

# Google Cloud Deployment Script for AI-Powered Rental Accommodation Platform

echo "🚀 Starting Google Cloud Deployment..."

# Check if gcloud CLI is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud CLI not found. Please install it first:"
    echo "   https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "🔐 Please authenticate with Google Cloud:"
    gcloud auth login
fi

# Set the project
echo "📋 Setting project to data-417505..."
gcloud config set project data-417505

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable appengine.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable vertex.googleapis.com

# Deploy to App Engine
echo "🚀 Deploying to Google App Engine..."
gcloud app deploy app.yaml --quiet

# Get the deployed URL
echo "✅ Deployment complete!"
echo "🌐 Your application is available at:"
gcloud app browse

echo ""
echo "📊 To view logs:"
echo "   gcloud app logs tail -s default"
echo ""
echo "🔧 To manage your app:"
echo "   gcloud app versions list"
echo "   gcloud app versions delete VERSION_ID"
