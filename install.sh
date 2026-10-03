#!/usr/bin/env bash
# Antigravity S-Tier Configuration Installer (macOS / Linux)
set -e

echo "=========================================================="
echo "  ANTIGRAVITY S-TIER ENTERPRISE SETUP INSTALLER (POSIX)   "
echo "=========================================================="

USER_HOME="$HOME"
GEMINI_DIR="$USER_HOME/.gemini"
CONFIG_DIR="$GEMINI_DIR/config"
SKILLS_DIR="$CONFIG_DIR/skills"
TEMPLATES_DIR="$GEMINI_DIR/templates"
PLUGINS_DIR="$CONFIG_DIR/plugins"
MCP_DIR="$GEMINI_DIR/mcp-servers"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "[1/6] Setting up directory structures..."
mkdir -p "$GEMINI_DIR" "$CONFIG_DIR" "$SKILLS_DIR" "$TEMPLATES_DIR" "$PLUGINS_DIR" "$MCP_DIR"

echo "[2/6] Installing 98+ S-Tier Skills..."
if [ -d "$SCRIPT_DIR/skills" ]; then
    cp -r "$SCRIPT_DIR/skills/"* "$SKILLS_DIR/"
    echo "  -> Skills installed to $SKILLS_DIR"
fi

echo "[3/6] Installing Guardrails & Templates..."
if [ -d "$SCRIPT_DIR/templates" ]; then
    cp -r "$SCRIPT_DIR/templates/"* "$TEMPLATES_DIR/"
    echo "  -> Templates installed to $TEMPLATES_DIR"
fi

echo "[4/6] Installing Global Rules (GEMINI.md & AGENTS.md)..."
if [ -d "$SCRIPT_DIR/rules" ]; then
    [ -f "$SCRIPT_DIR/rules/GEMINI.md" ] && cp "$SCRIPT_DIR/rules/GEMINI.md" "$GEMINI_DIR/"
    [ -f "$SCRIPT_DIR/rules/AGENTS.md" ] && cp "$SCRIPT_DIR/rules/AGENTS.md" "$GEMINI_DIR/"
    echo "  -> Rules synced to $GEMINI_DIR"
fi

echo "[5/6] Installing Plugins..."
if [ -d "$SCRIPT_DIR/plugins" ]; then
    cp -r "$SCRIPT_DIR/plugins/"* "$PLUGINS_DIR/"
    echo "  -> Plugins synced to $PLUGINS_DIR"
fi

echo "[6/6] Configuring MCP Servers..."
if [ -d "$SCRIPT_DIR/mcp/custom-servers" ]; then
    cp -r "$SCRIPT_DIR/mcp/custom-servers/"* "$MCP_DIR/"
    echo "  -> Custom MCP servers copied to $MCP_DIR"
fi

TEMPLATE_FILE="$SCRIPT_DIR/mcp/mcp_config.template.json"
TARGET_MCP_CONFIG="$CONFIG_DIR/mcp_config.json"

if [ -f "$TEMPLATE_FILE" ]; then
    if [ -f "$TARGET_MCP_CONFIG" ]; then
        cp "$TARGET_MCP_CONFIG" "$TARGET_MCP_CONFIG.bak"
        echo "  -> Backed up existing config to .bak"
    fi
    sed -e "s|{{USER_HOME}}|$USER_HOME|g" \
        -e "s|{{USER_HOME}}\\\\security_repos|$MCP_DIR|g" \
        "$TEMPLATE_FILE" > "$TARGET_MCP_CONFIG"
    echo "  -> Generated $TARGET_MCP_CONFIG"
fi

echo "[7/8] Installing Epistemic Lessons & Incident Postmortems..."
GODKILLER_DIR="$GEMINI_DIR/godkiller_data"
mkdir -p "$GODKILLER_DIR"
if [ -f "$SCRIPT_DIR/lessons/lessons.db" ]; then
    cp "$SCRIPT_DIR/lessons/lessons.db" "$GODKILLER_DIR/lessons.db"
    echo "  -> Epistemic lessons database synced to $GODKILLER_DIR/lessons.db"
fi
if [ -d "$SCRIPT_DIR/lessons/ui_artifacts" ]; then
    mkdir -p "$GODKILLER_DIR/arena/results/ui_artifacts"
    cp -r "$SCRIPT_DIR/lessons/ui_artifacts/"* "$GODKILLER_DIR/arena/results/ui_artifacts/"
    echo "  -> Synced 21 QA journey verification manifests"
fi

echo "[8/8] Installing Antigravity System Internals (MCP Schemas, Builtins, Tools)..."
AG_SYSTEM_DIR="$GEMINI_DIR/antigravity"
mkdir -p "$AG_SYSTEM_DIR"
if [ -d "$SCRIPT_DIR/antigravity-system" ]; then
    cp -r "$SCRIPT_DIR/antigravity-system/"* "$AG_SYSTEM_DIR/"
    echo "  -> Antigravity MCP schemas & built-in system deployed to $AG_SYSTEM_DIR"
fi

echo "=========================================================="
echo "  INSTALLATION COMPLETE! ANTIGRAVITY IS S-TIER READY      "
echo "=========================================================="
