"""
Expense Categorization for ATO Compliance
"""
from typing import Dict, Any


class ExpenseCategorizer:
    """Categorize expenses based on vendor, description, and line items"""
    
    # Enhanced categories with comprehensive keywords
    CATEGORIES = {
        "Food & Groceries": [
            "food", "grocery", "groceries", "supermarket", "woolworths", "coles", 
            "aldi", "iga", "restaurant", "cafe", "coffee", "lunch", "dinner", 
            "breakfast", "meal", "catering", "uber eats", "menulog", "deliveroo", 
            "doordash", "hungry jack", "mcdonald", "kfc", "subway", "domino"
        ],
        "Electronics": [
            "electronics", "electronic", "jb hi-fi", "jb hifi", "harvey norman", 
            "good guys", "bing lee", "appliance", "tv", "television", "camera", 
            "headphones", "speaker", "audio", "video", "gaming", "console", 
            "playstation", "xbox", "nintendo"
        ],
        "Software & Subscriptions": [
            "software", "license", "subscription", "saas", "ide", "github", "azure", 
            "aws", "jetbrains", "microsoft", "adobe", "npm", "python", "annual", 
            "monthly", "cloud", "hosting", "domain", "ssl", "api", "dropbox", 
            "google workspace", "office 365", "slack", "zoom", "notion", "figma", 
            "canva", "visual studio", "intellij", "pycharm", "webstorm"
        ],
        "Computer Equipment": [
            "computer", "laptop", "monitor", "keyboard", "mouse", "hardware", "dell", 
            "hp", "lenovo", "macbook", "ipad", "tablet", "printer", "scanner", 
            "webcam", "microphone", "usb", "cable", "adapter", "dock", "ssd", 
            "hard drive", "ram", "memory", "cpu", "gpu", "motherboard"
        ],
        "Electricity": [
            "electricity", "energy", "power", "electric", "eora", "ergon", "ausgrid", 
            "energex", "agl", "origin", "red energy", "simply energy", "alinta", 
            "powershop", "momentum energy"
        ],
        "Internet": [
            "internet", "isp", "broadband", "nbn", "telstra", "optus", "vodafone", 
            "data", "tpg", "aussie broadband", "superloop", "belong", "wifi", 
            "modem", "router", "dodo", "iinet"
        ],
        "Phone & Mobile": [
            "phone", "mobile", "telco", "mobile plan", "sim", "smartphone", "iphone", 
            "samsung", "android", "prepaid", "postpaid", "amaysim", "boost", 
            "kogan mobile", "catch connect", "aldi mobile"
        ],
        "Professional Development": [
            "training", "course", "udemy", "pluralsight", "education", "conference", 
            "seminar", "masterclass", "workshop", "certification", "exam", "learning", 
            "tutorial", "bootcamp", "coursera", "linkedin learning", "skillshare", 
            "codecademy", "treehouse", "datacamp"
        ],
        "Professional Membership": [
            "association", "membership", "professional", "society", "aca", "ieee", 
            "acm", "annual fee", "registration", "accreditation", "acs", "aia"
        ],
        "Office Supplies": [
            "office", "stationery", "supplies", "paper", "pen", "desk", "chair", 
            "filing", "officeworks", "staples", "notebook", "folder", "binder", 
            "whiteboard", "marker", "ink", "toner", "cartridge"
        ],
        "Communication Tools": [
            "communication", "voip", "skype", "teams", "zoom", "slack", "discord", 
            "webex", "gotomeeting", "conferencing", "video call", "ringcentral", 
            "8x8", "dialpad"
        ],
        "Transportation": [
            "transport", "uber", "taxi", "lyft", "didi", "ola", "petrol", "fuel", 
            "gas", "parking", "toll", "car", "vehicle", "automotive", "service", 
            "maintenance", "registration", "rego", "ctp", "greenslip"
        ],
        "Clothing & Apparel": [
            "clothing", "clothes", "apparel", "shirt", "pants", "shoes", "jacket", 
            "dress", "fashion", "wear", "footwear", "uniqlo", "zara", "h&m", 
            "target", "kmart", "big w", "myer", "david jones"
        ],
        "Health & Medical": [
            "health", "medical", "doctor", "pharmacy", "chemist", "medicine", 
            "prescription", "dental", "dentist", "optometry", "glasses", 
            "physiotherapy", "physio", "hospital", "clinic", "medicare", "pbs"
        ],
        "Home & Garden": [
            "home", "garden", "bunnings", "mitre 10", "hardware", "tools", "paint", 
            "furniture", "ikea", "fantastic furniture", "homeware", "decor", 
            "renovation", "repair", "plumbing", "electrical"
        ],
        "Entertainment & Media": [
            "entertainment", "netflix", "spotify", "disney", "amazon prime", "stan", 
            "binge", "kayo", "foxtel", "streaming", "music", "movie", "cinema", 
            "theatre", "event", "ticket", "concert", "apple music", "youtube premium"
        ],
        "Books & Publications": [
            "book", "books", "publication", "magazine", "journal", "kindle", "ebook", 
            "audiobook", "audible", "bookstore", "dymocks", "booktopia", "amazon books", 
            "scribd", "o'reilly"
        ],
        "Insurance": [
            "insurance", "policy", "premium", "cover", "coverage", "life insurance", 
            "health insurance", "car insurance", "home insurance", "contents insurance", 
            "income protection"
        ],
        "Banking & Finance": [
            "bank", "banking", "fee", "account fee", "transaction fee", "atm", 
            "interest", "loan", "credit card", "debit card", "financial", "investment", 
            "commonwealth", "westpac", "anz", "nab"
        ],
        "Utilities & Services": [
            "utility", "utilities", "water", "gas", "sewerage", "council", "rates", 
            "waste", "garbage", "bin", "service fee", "sydney water", "yarra valley water"
        ]
    }
    
    def categorize(self, vendor_name: str, description: str, line_items: list) -> str:
        """
        Categorize expense based on vendor, description, and line items
        
        Args:
            vendor_name: Vendor/supplier name
            description: Invoice description
            line_items: List of line items
        
        Returns:
            Category name
        """
        # Combine all text for searching
        search_text = f"{vendor_name} {description}"
        
        # Add line item descriptions
        for item in line_items:
            if isinstance(item, dict) and 'description' in item:
                search_text += f" {item['description']}"
        
        search_text = search_text.lower()
        
        # Search for category matches
        for category, keywords in self.CATEGORIES.items():
            for keyword in keywords:
                if keyword in search_text:
                    return category
        
        return "Other"
    
    @staticmethod
    def get_all_categories() -> list:
        """Get list of all available categories"""
        return list(ExpenseCategorizer.CATEGORIES.keys()) + ["Other"]
