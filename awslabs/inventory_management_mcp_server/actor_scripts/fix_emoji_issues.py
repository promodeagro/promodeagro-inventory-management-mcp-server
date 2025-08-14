#!/usr/bin/env python3
"""
Fix Emoji Issues in Actor Scripts
Replaces all emoji characters with text equivalents to fix Windows console encoding issues.
"""

import os
import re
from typing import Dict

def get_emoji_replacements() -> Dict[str, str]:
    """Get mapping of emoji characters to text replacements"""
    return {
        # Common emojis
        '🔐': '[AUTH]',
        '🏢': '[ACCOUNT]',
        '🌍': '[REGION]',
        '💡': '[TIP]',
        '👤': '[USER]',
        '🔒': '[PASSWORD]',
        '📧': '[EMAIL]',
        '📅': '[DATE]',
        '🆔': '[ID]',
        '📋': '[MENU]',
        '🛒': '[CART]',
        '📦': '[ORDER]',
        '💳': '[PAYMENT]',
        '📝': '[FEEDBACK]',
        '🚪': '[EXIT]',
        '🎯': '[SELECT]',
        '🏷️': '[CATEGORY]',
        '🔍': '[SEARCH]',
        '👁️': '[VIEW]',
        '🛍️': '[SHOPPING]',
        '✅': '[SUCCESS]',
        '❌': '[ERROR]',
        '📊': '[STATS]',
        '⏱️': '[TIME]',
        '💰': '[PRICE]',
        '🎨': '[VARIANT]',
        '📏': '[SIZE]',
        '🌈': '[COLOR]',
        '⚖️': '[WEIGHT]',
        '📍': '[ADDRESS]',
        '🏠': '[HOME]',
        '➕': '[ADD]',
        '⏳': '[WAIT]',
        '📮': '[POSTAL]',
        '📱': '[MOBILE]',
        '🧹': '[CLEANUP]',
        '🔧': '[CONFIG]',
        '⚙️': '[SETTINGS]',
        '🕐': '[TIMEOUT]',
        '🌐': '[AWS]',
        '📁': '[HISTORY]',
        '🔙': '[BACK]',
        '🚀': '[START]',
        '🔄': '[PROCESS]',
        '⚠️': '[WARNING]',
        'ℹ️': '[INFO]',
        '🎬': '[ACTION]',
        '🎭': '[ACTOR]',
        '🏁': '[COMPLETE]',
        '🎉': '[SUCCESS]',
        '🔔': '[NOTIFY]',
        '📈': '[REPORT]',
        '💾': '[SAVE]',
        '🗑️': '[DELETE]',
        '🚮': '[CLEAR]',
        '❓': '[CONFIRM]',
        '⏭️': '[SKIP]',
        '🎮': '[INTERACTIVE]',
        '🔢': '[NUMBER]',
        '📤': '[OUTPUT]',
        '🚚': '[DELIVERY]',
        '🏭': '[WAREHOUSE]',
        '📊': '[ANALYTICS]',
        '🔍': '[AUDIT]',
        '💼': '[BUSINESS]',
        '🏪': '[SUPPLIER]',
        '🎯': '[TARGET]',
        '📋': '[CLIPBOARD]',
        '🔐': '[SECURE]',
        '🌟': '[STAR]',
        '⭐': '[RATING]',
        '🐛': '[BUG]',
        '💬': '[CHAT]',
        '🆘': '[HELP]',
        '🔧': '[TOOL]',
        '📞': '[CONTACT]',
        '🎪': '[DEMO]',
        '🧪': '[TEST]',
        '🎬': '[DEMO]',
        '🔄': '[MULTIPLE]',
        '🎮': '[INTERACTIVE]',
        '🧹': '[CLEANUP]',
        '👋': '[GOODBYE]',
        '⚠️': '[INTERRUPTED]',
        '🚨': '[ISSUE]',
        '🎓': '[DEMO]',
        '🔄': '[FLOW]',
        '🎭': '[ORCHESTRATE]',
        '📊': '[TRACK]',
        '📝': '[GENERATE]',
        '💡': '[NOTE]',
        '🔮': '[FUTURE]',
        '📞': '[SUPPORT]',
        '🎉': '[SUMMARY]'
    }

def fix_emoji_in_file(filepath: str) -> bool:
    """Fix emoji characters in a single file"""
    try:
        # Read the file
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Get emoji replacements
        replacements = get_emoji_replacements()
        
        # Track changes
        original_content = content
        changes_made = 0
        
        # Replace each emoji
        for emoji, replacement in replacements.items():
            if emoji in content:
                content = content.replace(emoji, replacement)
                changes_made += content.count(replacement) - original_content.count(replacement)
        
        # Write back if changes were made
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[FIXED] {os.path.basename(filepath)}: {changes_made} emoji replacements")
            return True
        else:
            print(f"[CLEAN] {os.path.basename(filepath)}: No emojis found")
            return False
            
    except Exception as e:
        print(f"[ERROR] {os.path.basename(filepath)}: {str(e)}")
        return False

def main():
    """Fix emoji issues in all actor scripts"""
    print("🔧 Fixing Emoji Issues in Actor Scripts")
    print("=" * 50)
    
    # List of script files to fix
    script_files = [
        'customer_portal_standalone.py',
        'inventory_staff_standalone.py',
        'warehouse_manager_standalone.py',
        'logistics_manager_standalone.py',
        'delivery_personnel_standalone.py',
        'supplier_portal_standalone.py',
        'auditor_standalone.py',
        'auth_manager.py',
        'complete_flow_orchestrator.py'
    ]
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    fixed_count = 0
    
    for script_file in script_files:
        filepath = os.path.join(current_dir, script_file)
        if os.path.exists(filepath):
            if fix_emoji_in_file(filepath):
                fixed_count += 1
        else:
            print(f"[SKIP] {script_file}: File not found")
    
    print("=" * 50)
    print(f"[COMPLETE] Fixed {fixed_count} out of {len(script_files)} files")
    print("All emoji characters have been replaced with text equivalents.")
    print("Scripts should now work without Unicode encoding issues.")

if __name__ == '__main__':
    main()

