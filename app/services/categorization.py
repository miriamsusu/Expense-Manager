from app.schemas.expense import Category

category_keywords:dict[Category, list[str]]={
    Category.groceries: ["walmart", "kroger", "safeway", "trader joe", "whole foods", "grocery"],
    Category.entertainment: ["netflix", "spotify", "cinema", "movie", "steam", "concert"],
    Category.gas: ["shell", "socar", "omw", "mol", "fuel"],
    Category.housing: ["rent", "mortgage", "landlord", "apartment"],
    Category.dining: ["restaurant", "starbucks", "mcdonald", "cafe", "pizza"],
    Category.utilities: ["electric", "water bill", "internet", "comcast", "verizon"],
}

def categorize(description: str)->Category:
    lowered=description.lower()
    for category,keywords in category_keywords.items():
        if any(key in lowered for key in keywords):
            return category
    return Category.other