#!/bin/bash

# AID Morning Startup Script
# Run this or use /good-morning in Claude Code

set -e

echo "═══════════════════════════════════════════════════════"
echo "           ☀️  AID STARTUP CHECK"
echo "═══════════════════════════════════════════════════════"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ============================================
# 1. DOCKER CHECK
# ============================================
echo "🐳 DOCKER"

if docker info > /dev/null 2>&1; then
    echo -e "   Status: ${GREEN}✅ Running${NC}"
    
    # Show running containers
    CONTAINERS=$(docker ps --format "{{.Names}}: {{.Status}}" 2>/dev/null | head -5)
    if [ -n "$CONTAINERS" ]; then
        echo "   Containers:"
        echo "$CONTAINERS" | while read line; do
            echo "   - $line"
        done
    else
        echo "   Containers: None running"
    fi
else
    echo -e "   Status: ${RED}❌ Not running${NC}"
    echo -e "   ${YELLOW}→ Start Docker Desktop${NC}"
fi
echo ""

# ============================================
# 2. MCP CHECKS
# ============================================
echo "🔌 MCP CONNECTIONS"
echo ""

# Figma MCP (local Dev Mode server)
echo -n "   Figma:     "
if curl -s --connect-timeout 2 http://127.0.0.1:3845/mcp > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Connected${NC}"
else
    echo -e "${RED}❌ Not connected${NC}"
    echo -e "              ${YELLOW}→ Open Figma Desktop, enable Dev Mode MCP${NC}"
fi

# Jira - check if token exists
echo -n "   Jira:      "
if [ -n "$JIRA_API_TOKEN" ] || [ -n "$ATLASSIAN_API_TOKEN" ]; then
    echo -e "${GREEN}✅ Token configured${NC}"
else
    echo -e "${YELLOW}⚠️  Token not set${NC}"
    echo -e "              ${YELLOW}→ Set JIRA_API_TOKEN or ATLASSIAN_API_TOKEN${NC}"
fi

# GitHub - check if gh is authenticated
echo -n "   GitHub:    "
if gh auth status > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Authenticated${NC}"
else
    echo -e "${YELLOW}⚠️  Not authenticated${NC}"
    echo -e "              ${YELLOW}→ Run: gh auth login${NC}"
fi

# Chrome DevTools (for browser automation)
echo -n "   Chrome:    "
if curl -s --connect-timeout 2 http://localhost:9222/json > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Debug port open${NC}"
else
    echo -e "${YELLOW}⚠️  Not running${NC}"
    echo -e "              ${YELLOW}→ chrome --remote-debugging-port=9222${NC}"
fi

echo ""

# ============================================
# 3. PROJECT STATE
# ============================================
echo "═══════════════════════════════════════════════════════"
echo ""
echo "📊 PROJECT STATE"
echo ""

if [ -f ".aid/state.json" ]; then
    # Parse state.json (requires jq)
    if command -v jq &> /dev/null; then
        PHASE=$(jq -r '.current_phase' .aid/state.json)
        PHASE_NAME=$(jq -r '.phase_name' .aid/state.json)
        STARTED=$(jq -r '.started_at' .aid/state.json)
        
        echo "   Current Phase: [$PHASE] $PHASE_NAME"
        echo "   Started: $STARTED"
    else
        echo "   State file exists: .aid/state.json"
        echo "   (Install jq for detailed parsing)"
    fi
else
    echo -e "   ${YELLOW}⚠️  No .aid/state.json found${NC}"
    echo "   Run /aid-init to initialize project phases"
fi

echo ""
echo "═══════════════════════════════════════════════════════"
echo ""
echo "Ready! Run 'claude' and use /good-morning for guided startup"
echo ""
