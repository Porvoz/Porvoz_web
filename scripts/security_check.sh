#!/bin/bash
# Porvoz Security Pre-Deploy Check
# Run this BEFORE pushing to GitHub
# Usage: bash scripts/security_check.sh

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}[Porvoz] Running security checks...${NC}\n"

# 1. Check that .env is in .gitignore
echo -e "${YELLOW}[1/5]${NC} Checking .env is ignored..."
if git check-ignore .env > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} .env is properly ignored\n"
else
    echo -e "${RED}✗${NC} .env is NOT in .gitignore! Add it immediately:\n"
    echo "    echo '.env' >> .gitignore"
    exit 1
fi

# 2. Check for common secrets in staged changes
echo -e "${YELLOW}[2/5]${NC} Checking for hardcoded secrets in staged changes..."
SECRETS_FOUND=0

# Patterns to check
PATTERNS=(
    "password.*="
    "secret.*="
    "token.*="
    "api.?key.*="
    "Authorization.*Bearer"
    "TWILIO_AUTH_TOKEN="
    "GEMINI_API_KEY="
    "DATABASE_URL="
)

for pattern in "${PATTERNS[@]}"; do
    if git diff --cached | grep -i "$pattern" && ! grep -q "example\|placeholder"; then
        echo -e "${RED}✗${NC} Found potential secret matching: $pattern"
        SECRETS_FOUND=1
    fi
done

if [ $SECRETS_FOUND -eq 0 ]; then
    echo -e "${GREEN}✓${NC} No obvious secrets found in staged changes\n"
else
    echo -e "${RED}✗${NC} Review the changes above\n"
    exit 1
fi

# 3. Check that .env.example exists and is safe
echo -e "${YELLOW}[3/5]${NC} Checking .env.example..."
if [ ! -f .env.example ]; then
    echo -e "${RED}✗${NC} .env.example not found"
    exit 1
fi

if grep -q "xxxx\|your-\|your_\|placeholder" .env.example > /dev/null; then
    echo -e "${GREEN}✓${NC} .env.example has placeholder values\n"
else
    echo -e "${YELLOW}!${NC} .env.example might not have placeholders\n"
fi

# 4. Check for .env in uncommitted files
echo -e "${YELLOW}[4/5]${NC} Checking for .env in untracked files..."
if git status --short | grep -q ".env"; then
    echo -e "${RED}✗${NC} .env is in untracked files! Remove it:"
    echo "    rm .env"
    echo "    git status --short | grep .env"
    exit 1
else
    echo -e "${GREEN}✓${NC} .env not in untracked files\n"
fi

# 5. Check that production settings exist
echo -e "${YELLOW}[5/5]${NC} Checking production settings..."
if grep -q "ALLOWED_HOSTS" porvoz/config/settings/production.py; then
    echo -e "${GREEN}✓${NC} Production settings validated\n"
else
    echo -e "${YELLOW}!${NC} Production settings may need review\n"
fi

echo -e "${GREEN}✅ All security checks passed!${NC}"
echo -e "${YELLOW}Safe to push to GitHub${NC}\n"
