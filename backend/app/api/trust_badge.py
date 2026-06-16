"""Public Trust Badge API - embeddable security badges for websites."""
from fastapi import APIRouter, Response, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from fastapi import Depends
from typing import Optional

from app.db.database import get_db
from app.models.public_check import PublicCheck
from app.models.asset import Asset
from datetime import datetime, timedelta


router = APIRouter(prefix="/api/trust-badge", tags=["Trust Badge"])


def generate_badge_svg(score: int, grade: str, verified: bool = True) -> str:
    """
    Generate SVG badge showing trust score - Africa Cyber Trust branded.

    Args:
        score: Security score (0-100)
        grade: Letter grade (A-F)
        verified: Whether the score is verified

    Returns:
        SVG markup with ACT brand colors (Blue #0047AB & Gold #DAA520)
    """
    # Brand colors
    BLUE = "#0047AB"
    GOLD = "#DAA520"

    # Grade color based on score
    if score >= 90:
        grade_color = "#10B981"  # Green - Excellent
    elif score >= 75:
        grade_color = BLUE  # Blue - Good
    elif score >= 60:
        grade_color = "#EAB308"  # Yellow - Fair
    elif score >= 40:
        grade_color = "#F97316"  # Orange - Poor
    else:
        grade_color = "#DC2626"  # Red - Critical

    verified_badge = f"""
    <circle cx="160" cy="15" r="4" fill="{GOLD}"/>
    <text x="168" y="19" font-size="10" fill="{BLUE}" font-weight="600">Verified</text>
    """ if verified else ""

    svg = f"""
    <svg width="240" height="90" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:{BLUE};stop-opacity:1" />
                <stop offset="100%" style="stop-color:{GOLD};stop-opacity:1" />
            </linearGradient>
            <filter id="shadow">
                <feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.2"/>
            </filter>
        </defs>

        <!-- Background with gradient border -->
        <rect width="240" height="90" rx="10" fill="url(#grad)"/>

        <!-- White inner background -->
        <rect x="3" y="3" width="234" height="84" rx="8" fill="#FFFFFF"/>

        <!-- ACT Shield Logo -->
        <g transform="translate(20, 35)">
            <!-- Shield outline -->
            <path d="M 15 0 L 25 5 L 25 18 Q 25 25 15 30 Q 5 25 5 18 L 5 5 Z"
                  fill="{BLUE}" opacity="0.15" stroke="{BLUE}" stroke-width="1.5"/>
            <!-- Shield accent -->
            <path d="M 15 5 L 20 7 L 20 16 Q 20 20 15 23 Q 10 20 10 16 L 10 7 Z"
                  fill="{GOLD}" opacity="0.4"/>
            <!-- Checkmark -->
            <path d="M 12 15 L 14 17 L 19 12"
                  stroke="{BLUE}" stroke-width="2" fill="none" stroke-linecap="round"/>
        </g>

        <!-- Score -->
        <text x="70" y="42" font-size="32" fill="{BLUE}" font-weight="bold">{score}</text>
        <text x="115" y="42" font-size="14" fill="#6B7280" font-weight="500">/100</text>

        <!-- Grade Badge -->
        <g transform="translate(145, 25)">
            <rect width="42" height="42" rx="6" fill="{grade_color}" filter="url(#shadow)"/>
            <text x="21" y="30" font-size="26" fill="#FFFFFF" text-anchor="middle" font-weight="bold">{grade}</text>
        </g>

        <!-- Label -->
        <text x="70" y="60" font-size="13" fill="#6B7280" font-weight="500">Security Score</text>

        {verified_badge}

        <!-- Branding -->
        <g transform="translate(10, 75)">
            <text x="0" y="0" font-size="9" fill="{BLUE}" font-weight="600">AFRICA CYBER TRUST</text>
            <circle cx="135" cy="-3" r="2.5" fill="{GOLD}"/>
            <text x="142" y="0" font-size="8" fill="#9CA3AF">Secured</text>
        </g>
    </svg>
    """
    return svg


def calculate_grade(score: int) -> str:
    """Convert score to letter grade."""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"


@router.get("/badge/{domain}.svg")
async def get_badge_svg(
    domain: str,
    db: Session = Depends(get_db)
):
    """
    Get SVG badge for a domain.

    Returns an SVG image showing the security score.
    Can be embedded in websites using <img src="...">.

    Example:
        <img src="https://api.africacybertrust.com/api/trust-badge/badge/example.com.svg" alt="Security Badge"/>
    """
    # Find latest public check for this domain
    check = db.query(PublicCheck).filter(
        PublicCheck.url.ilike(f"%{domain}%")
    ).order_by(PublicCheck.created_at.desc()).first()

    if not check or not check.result_data:
        # No score available - return pending badge
        svg = generate_badge_svg(0, "?", verified=False)
        return Response(content=svg, media_type="image/svg+xml")

    # Get score from check
    score = check.result_data.get("final_score", 0)
    grade = calculate_grade(score)

    # Check if score is recent (within 30 days)
    is_fresh = check.created_at > datetime.utcnow() - timedelta(days=30)

    svg = generate_badge_svg(score, grade, verified=is_fresh)
    return Response(content=svg, media_type="image/svg+xml")


@router.get("/widget/{domain}")
async def get_embeddable_widget(
    domain: str,
    theme: Optional[str] = "light",
    db: Session = Depends(get_db)
):
    """
    Get embeddable HTML widget showing trust score.

    Query params:
        theme: 'light' or 'dark'

    Returns HTML that can be embedded via iframe or directly.
    """
    # Find latest check
    check = db.query(PublicCheck).filter(
        PublicCheck.url.ilike(f"%{domain}%")
    ).order_by(PublicCheck.created_at.desc()).first()

    score = 0
    grade = "?"
    last_checked = "Never"
    verified = False

    if check and check.result_data:
        score = check.result_data.get("final_score", 0)
        grade = calculate_grade(score)
        last_checked = check.created_at.strftime("%b %d, %Y")
        verified = check.created_at > datetime.utcnow() - timedelta(days=30)

    # Brand colors
    BLUE = "#0047AB"
    GOLD = "#DAA520"

    # Color scheme
    if theme == "dark":
        bg_color = "#1F2937"
        text_color = "#F9FAFB"
        subtext_color = "#9CA3AF"
        border_color = "#374151"
        brand_gradient = f"linear-gradient(135deg, {BLUE} 0%, #1E40AF 100%)"
    else:
        bg_color = "#FFFFFF"
        text_color = "#111827"
        subtext_color = "#6B7280"
        border_color = "#E5E7EB"
        brand_gradient = f"linear-gradient(135deg, {BLUE} 0%, {GOLD} 100%)"

    # Score color based on grade
    if score >= 90:
        score_color = "#10B981"  # Green
    elif score >= 75:
        score_color = BLUE  # Blue (brand)
    elif score >= 60:
        score_color = "#EAB308"  # Yellow
    elif score >= 40:
        score_color = "#F97316"  # Orange
    else:
        score_color = "#DC2626"  # Red

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ margin: 0; padding: 10px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; }}
            .badge-container {{
                background: {bg_color};
                border: 2px solid {border_color};
                border-radius: 12px;
                padding: 20px;
                max-width: 300px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}
            .score-display {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 15px;
            }}
            .score {{
                font-size: 48px;
                font-weight: bold;
                color: {score_color};
            }}
            .grade {{
                background: {score_color};
                color: white;
                font-size: 32px;
                font-weight: bold;
                width: 60px;
                height: 60px;
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            .label {{
                color: {subtext_color};
                font-size: 14px;
                margin-bottom: 5px;
            }}
            .domain {{
                color: {text_color};
                font-size: 16px;
                font-weight: 600;
                margin-bottom: 10px;
                word-break: break-all;
            }}
            .verified {{
                display: flex;
                align-items: center;
                gap: 5px;
                color: {subtext_color};
                font-size: 12px;
            }}
            .verified-dot {{
                width: 8px;
                height: 8px;
                background: {score_color if verified else subtext_color};
                border-radius: 50%;
            }}
            .footer {{
                margin-top: 15px;
                padding-top: 15px;
                border-top: 1px solid {border_color};
                text-align: center;
            }}
            .footer a {{
                color: {BLUE};
                text-decoration: none;
                font-size: 12px;
                font-weight: 600;
            }}
            .footer a:hover {{
                text-decoration: underline;
            }}
        </style>
    </head>
    <body>
        <div class="badge-container">
            <div class="label">Security Score</div>
            <div class="score-display">
                <div class="score">{score}</div>
                <div class="grade">{grade}</div>
            </div>
            <div class="domain">{domain}</div>
            <div class="verified">
                <div class="verified-dot"></div>
                <span>{"Verified" if verified else "Unverified"} • Last checked: {last_checked}</span>
            </div>
            <div class="footer">
                <a href="https://www.africybertrust.com" target="_blank">Powered by Africa Cyber Trust</a>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


@router.get("/embed-code/{domain}")
async def get_embed_code(domain: str):
    """
    Get embed code snippet for website integration.

    Returns HTML/JS code that can be copy-pasted into websites.
    """
    badge_url = f"https://www.africybertrust.com/api/trust-badge/badge/{domain}.svg"
    widget_url = f"https://www.africybertrust.com/api/trust-badge/widget/{domain}"

    code_snippets = {
        "svg_badge": {
            "name": "SVG Badge (Lightweight)",
            "description": "Simple image badge, no iframe needed",
            "code": f'<a href="https://www.africybertrust.com/check/{domain}" target="_blank">\n    <img src="{badge_url}" alt="Security Badge" />\n</a>'
        },
        "widget_iframe": {
            "name": "Interactive Widget (Iframe)",
            "description": "Full widget with details",
            "code": f'<iframe src="{widget_url}" width="320" height="200" frameborder="0" style="border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);"></iframe>'
        },
        "widget_dark": {
            "name": "Dark Mode Widget",
            "description": "Widget with dark theme",
            "code": f'<iframe src="{widget_url}?theme=dark" width="320" height="200" frameborder="0" style="border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);"></iframe>'
        }
    }

    return {
        "domain": domain,
        "snippets": code_snippets,
        "preview_urls": {
            "badge": badge_url,
            "widget": widget_url
        }
    }
