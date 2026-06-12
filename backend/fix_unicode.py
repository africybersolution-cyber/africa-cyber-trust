#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix Unicode emoji and box-drawing characters in scan_service.py
Replace with ASCII equivalents that work in PDF.
"""

import re

def fix_recommendations():
    """Remove emojis and fix Unicode box characters."""

    file_path = 'app/services/scan_service.py'

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace box-drawing characters with ASCII
    # These are lines of repeated characters, so we need to handle the pattern
    content = re.sub(r'[━═]{3,}', '=' * 50, content)
    content = re.sub(r'[─]{3,}', '-' * 50, content)

    # Remove emojis (keep the text label only)
    content = content.replace('🔧 ', '')
    content = content.replace('✅ ', '')
    content = content.replace('⚠️  ', '')
    content = content.replace('⏱️  ', '')
    content = content.replace('💰 ', '')
    content = content.replace('📚 ', '')
    content = content.replace('📋 ', '')
    content = content.replace('🔗 ', '')

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("Fixed Unicode characters in scan_service.py")

if __name__ == "__main__":
    fix_unicode()
