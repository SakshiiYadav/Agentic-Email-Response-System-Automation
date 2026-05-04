"""
Sample customer emails covering diverse scenarios for demonstration.
"""

from datetime import datetime, timedelta

def _ts(hours_ago: int) -> str:
    return (datetime.now() - timedelta(hours=hours_ago)).strftime("%Y-%m-%d %H:%M")


SAMPLE_EMAILS = [
    {
        "sender":    "rajesh.kumar@gmail.com",
        "name":      "Rajesh Kumar",
        "subject":   "URGENT: My account has been hacked and I can't login!!",
        "body": (
            "I am writing this in complete panic. I got an email notification that my password "
            "was changed and now I can't log into my account. Someone has accessed my account "
            "without my permission and I believe they may have seen my payment details. "
            "This is completely unacceptable! I need this resolved IMMEDIATELY. "
            "I have been a customer for 5 years and this is how you treat me?! "
            "If this is not resolved today, I will be filing a complaint with the consumer "
            "protection authority and posting about this everywhere."
        ),
        "timestamp": _ts(1),
    },
    {
        "sender":    "priya.sharma@outlook.com",
        "name":      "Priya Sharma",
        "subject":   "Charged twice for my subscription - need refund",
        "body": (
            "Hello, I noticed that I was charged twice for my monthly subscription this month. "
            "I can see two transactions of $29.99 each on my credit card statement on March 15th. "
            "I have been trying to resolve this for the past week but keep getting generic responses. "
            "This is frustrating. Could you please look into this and process a refund for the "
            "duplicate charge? My order ID is ORD-2024-8832. Thank you."
        ),
        "timestamp": _ts(3),
    },
    {
        "sender":    "mike.johnson@company.co",
        "name":      "Mike Johnson",
        "subject":   "Question about bulk order pricing",
        "body": (
            "Hi there, I am reaching out on behalf of our company. We are looking to place "
            "a bulk order of approximately 500 units of your Product X model. "
            "Could you please provide information on: "
            "1. Volume discount pricing for orders above 200 and 500 units "
            "2. Lead time for bulk orders "
            "3. Whether you offer net-30 payment terms for business accounts "
            "4. Availability of custom branding/white-label options "
            "Looking forward to your response. Best regards, Mike Johnson, Procurement Manager"
        ),
        "timestamp": _ts(5),
    },
    {
        "sender":    "lisa.wong@email.com",
        "name":      "Lisa Wong",
        "subject":   "Package still not delivered after 3 weeks",
        "body": (
            "I placed an order (Order #ORD-7791) on February 20th and was given a delivery "
            "estimate of 5-7 business days. It has now been over 3 weeks and my package has "
            "still not arrived. The tracking page has shown 'In Transit' for the past 10 days "
            "with no updates. I have already contacted you twice and was told someone would "
            "follow up, but I have heard nothing. I need this resolved — either send a replacement "
            "or give me a full refund. I am very disappointed with this experience."
        ),
        "timestamp": _ts(8),
    },
    {
        "sender":    "sarah.m@personal.net",
        "name":      "Sarah M",
        "subject":   "Just wanted to say thank you!",
        "body": (
            "Hello! I just wanted to take a moment to thank your support team, especially "
            "Tom who helped me last week. He went above and beyond to resolve my issue and "
            "was incredibly patient and professional throughout. I rarely take the time to "
            "write positive feedback but this experience genuinely made my day. "
            "You have a loyal customer for life. Keep up the amazing work! "
            "Warmly, Sarah"
        ),
        "timestamp": _ts(12),
    },
    {
        "sender":    "david.patel@techcorp.io",
        "name":      "David Patel",
        "subject":   "App crashing on iOS 17 — critical bug",
        "body": (
            "Your mobile app is crashing every time I try to open the dashboard on iOS 17.2. "
            "This started after your last update (version 4.2.1). "
            "Steps to reproduce: Open app > Tap Dashboard > App crashes immediately. "
            "Device: iPhone 14 Pro, iOS 17.2 "
            "I rely on this app for my business and this is costing me real money every hour "
            "it doesn't work. Please treat this as a critical bug and provide a fix or workaround ASAP. "
            "Error log attached separately."
        ),
        "timestamp": _ts(2),
    },
    {
        "sender":    "ananya.r@university.edu",
        "name":      "Ananya R",
        "subject":   "How do I upgrade my plan?",
        "body": (
            "Hi, I am currently on the Basic plan and would like to upgrade to the Pro plan. "
            "I have a few questions before I do: "
            "1. Will my current data and settings be preserved after upgrading? "
            "2. Is the upgrade effective immediately or from the next billing cycle? "
            "3. Can I downgrade back if I change my mind, and are there any penalties? "
            "Thank you for your help!"
        ),
        "timestamp": _ts(18),
    },
    {
        "sender":    "angry.customer@mail.com",
        "name":      "Robert Chen",
        "subject":   "This is absolutely ridiculous — THIRD time contacting you",
        "body": (
            "I have contacted your support three times now and my issue is STILL not resolved. "
            "This is the most incompetent customer service I have ever experienced. "
            "My issue: I returned a product on Jan 5th, got a confirmation email, "
            "but my refund of $149.99 has not been processed after 6 weeks. "
            "Every time I contact you I get a different story. First it was '5 business days', "
            "then '10 business days', now apparently it's 'under review'. "
            "I am done waiting. Either process my refund TODAY or I will dispute this "
            "with my credit card company and leave detailed reviews on every platform I can find."
        ),
        "timestamp": _ts(0.5),
    },
]
