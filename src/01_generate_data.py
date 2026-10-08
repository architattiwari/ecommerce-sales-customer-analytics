"""Step 1: generate a synthetic e-commerce dataset (raw CSV files).

Everything here is fictional: names, emails, products and numbers.
A small number of data-quality problems are added on purpose so that
step 2 (02_clean_data.py) has something real to clean.
"""
import numpy as np
import pandas as pd

from common import RAW_DIR

SEED = 42
N_CUSTOMERS = 20_000
N_PRODUCTS = 5_000
N_ORDERS = 100_000
START_DATE = pd.Timestamp("2025-01-01")
END_DATE = pd.Timestamp("2025-12-31")

rng = np.random.default_rng(SEED)

# ---------------------------------------------------------------------------
# Reference data
# ---------------------------------------------------------------------------
# category: share of products, cost as a share of price, and subcategories as
# (typical price in INR, price spread, product types)
CATALOG = {
    "Electronics": {"share": 0.14, "cost_ratio": (0.78, 0.90), "subcategories": {
        "Smartphones": (14000, 0.55, ["Smartphone 128GB", "Smartphone 256GB", "5G Smartphone", "Smartphone 64GB"]),
        "Laptops": (45000, 0.35, ["Laptop 14 inch", "Gaming Laptop", "Ultrabook", "Laptop 15.6 inch"]),
        "Headphones & Earbuds": (2500, 0.80, ["Wireless Earbuds", "Over-Ear Headphones", "Neckband Earphones", "Gaming Headset"]),
        "Smart Watches": (3500, 0.70, ["Smart Watch", "Fitness Band", "Kids Smart Watch"]),
        "Televisions": (22000, 0.50, ["Smart TV 43 inch", "Smart TV 55 inch", "LED TV 32 inch", "4K Smart TV 50 inch"]),
        "Mobile Accessories": (500, 0.70, ["USB-C Cable", "Fast Charger", "Power Bank 10000mAh", "Phone Case", "Screen Guard"]),
    }},
    "Fashion": {"share": 0.20, "cost_ratio": (0.42, 0.58), "subcategories": {
        "Men's Clothing": (900, 0.50, ["Cotton T-Shirt", "Slim Fit Jeans", "Formal Shirt", "Hooded Sweatshirt", "Chino Trousers"]),
        "Women's Clothing": (1100, 0.55, ["Kurti", "Printed Dress", "Palazzo Set", "Cotton Saree", "Denim Jacket"]),
        "Footwear": (1800, 0.55, ["Running Shoes", "Casual Sneakers", "Leather Sandals", "Formal Shoes", "Slip-on Loafers"]),
        "Bags & Accessories": (1300, 0.60, ["Backpack", "Handbag", "Wallet", "Sunglasses", "Analog Watch"]),
    }},
    "Home & Kitchen": {"share": 0.16, "cost_ratio": (0.58, 0.74), "subcategories": {
        "Cookware": (1500, 0.55, ["Non-stick Pan", "Pressure Cooker", "Cookware Set", "Tawa", "Kadai"]),
        "Kitchen Appliances": (4000, 0.60, ["Mixer Grinder", "Air Fryer", "Electric Kettle", "Induction Cooktop", "Toaster"]),
        "Furniture": (7000, 0.70, ["Office Chair", "Bookshelf", "Study Table", "Shoe Rack", "Folding Bed"]),
        "Home Decor": (700, 0.60, ["Wall Clock", "Table Lamp", "Photo Frame Set", "Cushion Cover Set", "Curtains"]),
    }},
    "Beauty & Personal Care": {"share": 0.12, "cost_ratio": (0.38, 0.55), "subcategories": {
        "Skincare": (500, 0.50, ["Face Serum", "Moisturizer", "Sunscreen SPF 50", "Face Wash", "Night Cream"]),
        "Haircare": (400, 0.50, ["Shampoo", "Hair Oil", "Conditioner", "Hair Mask"]),
        "Makeup": (600, 0.55, ["Lipstick", "Foundation", "Kajal", "Compact Powder", "Eyeliner"]),
        "Grooming": (1500, 0.70, ["Beard Trimmer", "Hair Dryer", "Electric Shaver", "Epilator"]),
    }},
    "Books": {"share": 0.10, "cost_ratio": (0.58, 0.70), "subcategories": {
        "Fiction": (350, 0.30, ["Mystery Novel", "Romance Novel", "Fantasy Novel", "Thriller Novel"]),
        "Non-Fiction": (400, 0.30, ["Biography", "Self-Help Book", "History Book", "Business Book"]),
        "Academic & Exam Prep": (600, 0.40, ["Engineering Guide", "Aptitude Test Book", "Science Textbook", "Mock Test Series"]),
        "Children's Books": (250, 0.30, ["Picture Book", "Story Collection", "Activity Book", "Comic Book"]),
    }},
    "Sports & Fitness": {"share": 0.08, "cost_ratio": (0.55, 0.70), "subcategories": {
        "Fitness Equipment": (2500, 0.70, ["Dumbbell Set", "Yoga Mat", "Resistance Bands", "Treadmill", "Skipping Rope"]),
        "Outdoor Sports": (1800, 0.60, ["Cricket Bat", "Football", "Badminton Racket", "Cycling Helmet", "Trekking Backpack"]),
        "Sportswear": (1200, 0.50, ["Track Pants", "Sports T-Shirt", "Compression Tights", "Gym Shorts"]),
    }},
    "Toys & Games": {"share": 0.06, "cost_ratio": (0.52, 0.68), "subcategories": {
        "Board Games": (800, 0.50, ["Strategy Board Game", "Family Card Game", "Puzzle 1000 Pieces", "Chess Set"]),
        "Educational Toys": (700, 0.50, ["Building Blocks", "Science Kit", "Alphabet Learning Set", "Maths Game"]),
        "Action Figures & Dolls": (600, 0.55, ["Action Figure", "Fashion Doll", "Soft Toy", "Doll House"]),
        "Remote Control Toys": (1500, 0.60, ["RC Car", "RC Helicopter", "RC Stunt Bike", "Drone Toy"]),
    }},
    "Grocery": {"share": 0.14, "cost_ratio": (0.80, 0.90), "subcategories": {
        "Staples": (300, 0.60, ["Basmati Rice 5kg", "Atta 10kg", "Toor Dal 1kg", "Cooking Oil 5L", "Sugar 5kg"]),
        "Snacks & Beverages": (150, 0.50, ["Namkeen Combo", "Green Tea Pack", "Instant Coffee", "Dark Chocolate Box", "Cookies Pack"]),
        "Dry Fruits": (700, 0.50, ["Almonds 500g", "Cashews 500g", "Mixed Dry Fruits 1kg", "Raisins 500g"]),
        "Packaged Foods": (200, 0.50, ["Instant Noodles Pack", "Pasta Pack", "Pasta Sauce", "Breakfast Cereal"]),
    }},
}
CATEGORIES = list(CATALOG.keys())

BRANDS = ["Zenix", "Aurora", "Kiwa", "Nordale", "Pexo", "Vanta", "Luma", "Orbit", "Helio", "Tarsa",
          "Bluepeak", "Casa Nova", "Urbane", "Maple Lane", "Ryko", "Solace", "Trueline", "Everly",
          "Novo", "Cedar & Co", "Skyline", "Fable", "Ardent", "Mosaic", "Prism", "Kalpa", "Indigo Hill",
          "Veda", "Amara", "Brightly"]
VARIANTS = ["Pro", "Lite", "Plus", "Max", "Classic", "Essential", "Prime", "Elite", "Smart", "Ultra", "Neo", "Air"]

FIRST_NAMES = ["Aarav", "Vivaan", "Aditya", "Arjun", "Rohan", "Kabir", "Ishaan", "Rahul", "Karan", "Siddharth",
               "Ananya", "Diya", "Priya", "Sneha", "Kavya", "Isha", "Meera", "Neha", "Pooja", "Riya",
               "Aisha", "Fatima", "Imran", "Zoya", "Gurpreet", "Harleen", "Manpreet", "Jasleen", "Arun", "Lakshmi",
               "Suresh", "Divya", "Vikram", "Nisha", "Amit", "Sunita", "Rajesh", "Deepa", "Manoj", "Swati",
               "Tanvi", "Yash", "Varun", "Shreya", "Nikhil", "Aditi", "Pranav", "Simran", "Harsh", "Mehak"]
LAST_NAMES = ["Sharma", "Verma", "Gupta", "Singh", "Patel", "Mehta", "Shah", "Joshi", "Iyer", "Nair",
              "Reddy", "Rao", "Das", "Banerjee", "Chatterjee", "Kapoor", "Malhotra", "Khan", "Ahmed", "Ansari",
              "Kulkarni", "Deshmukh", "Pillai", "Menon", "Agarwal", "Bansal", "Jain", "Chauhan", "Yadav", "Mishra",
              "Pandey", "Tiwari", "Bhatt", "Thakur", "Saxena", "Sethi", "Chopra", "Bose", "Sinha", "Kaur"]

# city, state, relative weight (share of customers), delivery zone
LOCATIONS = [
    ("Mumbai", "Maharashtra", 9, "metro"), ("Pune", "Maharashtra", 4, "metro"), ("Nagpur", "Maharashtra", 1.5, "tier2"),
    ("Delhi", "Delhi", 9, "metro"), ("Bengaluru", "Karnataka", 8, "metro"), ("Mysuru", "Karnataka", 1, "tier2"),
    ("Hyderabad", "Telangana", 5, "metro"), ("Chennai", "Tamil Nadu", 5, "metro"), ("Coimbatore", "Tamil Nadu", 1.5, "tier2"),
    ("Kolkata", "West Bengal", 4, "metro"), ("Siliguri", "West Bengal", 0.8, "remote"),
    ("Ahmedabad", "Gujarat", 4, "metro"), ("Surat", "Gujarat", 2.5, "tier2"), ("Vadodara", "Gujarat", 1, "tier2"),
    ("Jaipur", "Rajasthan", 3.5, "tier2"), ("Jodhpur", "Rajasthan", 1.2, "tier2"), ("Udaipur", "Rajasthan", 1, "remote"),
    ("Lucknow", "Uttar Pradesh", 3, "tier2"), ("Kanpur", "Uttar Pradesh", 1.5, "tier2"),
    ("Noida", "Uttar Pradesh", 2.5, "metro"), ("Varanasi", "Uttar Pradesh", 1, "tier2"),
    ("Gurugram", "Haryana", 3, "metro"), ("Faridabad", "Haryana", 1, "tier2"),
    ("Chandigarh", "Chandigarh", 1.5, "tier2"), ("Ludhiana", "Punjab", 1.5, "tier2"), ("Amritsar", "Punjab", 1, "tier2"),
    ("Indore", "Madhya Pradesh", 2.5, "tier2"), ("Bhopal", "Madhya Pradesh", 2, "tier2"),
    ("Patna", "Bihar", 2, "tier2"), ("Bhubaneswar", "Odisha", 1.5, "tier2"),
    ("Kochi", "Kerala", 2.5, "tier2"), ("Thiruvananthapuram", "Kerala", 1.5, "tier2"),
    ("Guwahati", "Assam", 1.2, "remote"), ("Ranchi", "Jharkhand", 1, "remote"),
    ("Dehradun", "Uttarakhand", 1, "remote"), ("Srinagar", "Jammu & Kashmir", 0.5, "remote"),
    ("Panaji", "Goa", 0.8, "remote"),
]
locations = pd.DataFrame(LOCATIONS, columns=["city", "state", "weight", "zone"])
location_probs = (locations["weight"] / locations["weight"].sum()).to_numpy()

SEGMENTS = ["Standard", "Premium", "Student", "Business"]
SEGMENT_PROBS = [0.60, 0.15, 0.15, 0.10]
SEGMENT_ACTIVITY = {"Standard": 1.0, "Premium": 2.0, "Student": 0.8, "Business": 1.5}

PAYMENT_METHODS = ["UPI", "Credit Card", "Debit Card", "Cash on Delivery", "Net Banking", "Wallet"]
PAYMENT_PROBS = [0.38, 0.22, 0.15, 0.17, 0.05, 0.03]

# Order line behaviour, same order as CATEGORIES
CATEGORY_LINE_PROBS = [0.13, 0.21, 0.16, 0.13, 0.08, 0.07, 0.05, 0.17]
QUANTITY_PROBS = [
    [0.93, 0.06, 0.01, 0, 0], [0.60, 0.30, 0.10, 0, 0], [0.70, 0.22, 0.08, 0, 0], [0.60, 0.28, 0.12, 0, 0],
    [0.55, 0.30, 0.15, 0, 0], [0.80, 0.15, 0.05, 0, 0], [0.70, 0.22, 0.08, 0, 0], [0.35, 0.30, 0.20, 0.10, 0.05],
]
DISCOUNT_LEVELS = np.array([0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40])
DISCOUNT_PROBS = [
    [0.35, 0.22, 0.20, 0.12, 0.07, 0.03, 0.01, 0.00], [0.15, 0.10, 0.15, 0.15, 0.18, 0.12, 0.10, 0.05],
    [0.30, 0.18, 0.18, 0.14, 0.10, 0.06, 0.04, 0.00], [0.25, 0.18, 0.20, 0.15, 0.10, 0.07, 0.05, 0.00],
    [0.50, 0.20, 0.15, 0.10, 0.05, 0.00, 0.00, 0.00], [0.30, 0.18, 0.18, 0.14, 0.10, 0.07, 0.03, 0.00],
    [0.25, 0.15, 0.18, 0.15, 0.12, 0.08, 0.05, 0.02], [0.55, 0.20, 0.15, 0.07, 0.03, 0.00, 0.00, 0.00],
]
FESTIVE_DISCOUNT_BOOST = np.array([0.6, 0.8, 1.0, 1.2, 1.5, 1.8, 2.2, 2.5])
FESTIVE_MONTHS = [10, 11]

CATEGORY_QUALITY_OFFSET = {"Electronics": -0.10, "Fashion": -0.15, "Toys & Games": -0.20, "Books": 0.15, "Beauty & Personal Care": -0.05}
WEAK_SUBCATEGORIES = ["Smart Watches", "Footwear", "Remote Control Toys"]

REVIEW_TEXT = {
    5: ["Excellent quality, totally worth the price.", "Loved it! Arrived well packed.", "Exactly as described. Highly recommend.", "Great product, fast delivery."],
    4: ["Good product overall, happy with the purchase.", "Nice quality for the price.", "Works well. Delivery was fine.", "Good value, would buy again."],
    3: ["Average product. Does the job.", "Okay for the price, nothing special.", "Packaging could be better.", "Decent but expected a bit more."],
    2: ["Not as good as the pictures.", "Quality is below expectations.", "Delivery was late and product is average.", "Disappointed, may return."],
    1: ["Very poor quality. Not recommended.", "Stopped working quickly.", "Waste of money.", "Terrible experience, product was damaged."],
}


# ---------------------------------------------------------------------------
# Products and customers
# ---------------------------------------------------------------------------
def make_price(typical_price, spread):
    price = typical_price * rng.lognormal(0, spread)
    if price < 100:
        return max(19.0, round(price))
    return float(max(49, round(price / 10) * 10 - 1))


def generate_products():
    rows = []
    used_names = set()
    for category, info in CATALOG.items():
        subcategories = list(info["subcategories"].items())
        for i in range(round(N_PRODUCTS * info["share"])):
            subcategory, (typical_price, spread, product_types) = subcategories[i % len(subcategories)]
            name = f"{rng.choice(BRANDS)} {rng.choice(product_types)} {rng.choice(VARIANTS)}"
            while name in used_names:
                name = f"{name} {rng.integers(2, 99)}"
            used_names.add(name)

            unit_price = make_price(typical_price, spread)
            low, high = info["cost_ratio"]
            popularity = rng.lognormal(0, 0.9) * (unit_price / typical_price) ** -0.3
            if rng.random() < 0.08:
                popularity *= 0.05          # a few products that barely sell
            quality = rng.normal(4.15, 0.30) + CATEGORY_QUALITY_OFFSET.get(category, 0)
            if subcategory in WEAK_SUBCATEGORIES:
                quality -= 0.5
            rows.append([name, category, subcategory, unit_price, round(unit_price * rng.uniform(low, high), 2),
                         popularity, quality])

    products = pd.DataFrame(rows, columns=["product_name", "category", "subcategory", "unit_price", "cost_price",
                                           "popularity", "quality"])
    products.insert(0, "product_id", [f"P{i:04d}" for i in range(1, len(products) + 1)])
    return products


def generate_customers():
    first = rng.choice(FIRST_NAMES, N_CUSTOMERS)
    last = rng.choice(LAST_NAMES, N_CUSTOMERS)
    customer_ids = [f"C{i:05d}" for i in range(1, N_CUSTOMERS + 1)]
    location_index = rng.choice(len(locations), N_CUSTOMERS, p=location_probs)

    # signups run from Jan 2023 to mid Dec 2025, slightly more towards the end
    signup_offset = (rng.beta(1.1, 1.0, N_CUSTOMERS) * 1079).astype(int)
    customers = pd.DataFrame({
        "customer_id": customer_ids,
        "customer_name": first + " " + last,
        "email": [f"{f.lower()}.{l.lower()}{i}@example.com" for f, l, i in zip(first, last, range(1, N_CUSTOMERS + 1))],
        "city": locations["city"].to_numpy()[location_index],
        "state": locations["state"].to_numpy()[location_index],
        "signup_date": pd.Timestamp("2023-01-01") + pd.to_timedelta(signup_offset, unit="D"),
        "customer_segment": rng.choice(SEGMENTS, N_CUSTOMERS, p=SEGMENT_PROBS),
    })
    customers["location_index"] = location_index
    return customers


# ---------------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------------
def sample_from_table(prob_table, row_index):
    """Draw one category index per row from a table of probabilities."""
    table = np.array(prob_table, dtype=float)
    table = table / table.sum(axis=1, keepdims=True)
    cumulative = np.cumsum(table, axis=1)[row_index]
    draws = rng.random(len(row_index))[:, None]
    return np.minimum((draws > cumulative).sum(axis=1), table.shape[1] - 1)


def pick_order_dates(customers, order_customer_index):
    """Choose an order date for each order, never before the customer signed up."""
    days = pd.date_range(START_DATE, END_DATE)
    month_weight = {1: 0.90, 2: 0.85, 3: 0.95, 4: 0.95, 5: 1.0, 6: 0.90,
                    7: 0.95, 8: 1.05, 9: 1.0, 10: 1.40, 11: 1.35, 12: 1.05}
    weights = days.month.map(month_weight).to_numpy() * np.linspace(1.0, 1.15, len(days))
    weights = weights * np.where(days.dayofweek >= 5, 1.15, 1.0)

    cdf = np.cumsum(weights / weights.sum())
    cdf_before = np.concatenate([[0], cdf[:-1]])
    signup_day = (customers["signup_date"] - START_DATE).dt.days.clip(lower=0, upper=len(days) - 1).to_numpy()
    lower = cdf_before[signup_day[order_customer_index]]
    draws = lower + rng.random(len(order_customer_index)) * (1 - lower)
    day_index = np.minimum(np.searchsorted(cdf, draws), len(days) - 1)

    hour_probs = np.array([1, 1, 1, 1, 1, 2, 3, 4, 5, 6, 6, 6, 6, 6, 6, 6, 6, 7, 8, 9, 10, 9, 6, 3], dtype=float)
    hours = rng.choice(24, len(day_index), p=hour_probs / hour_probs.sum())
    seconds = rng.integers(0, 3600, len(day_index))
    return days[day_index] + pd.to_timedelta(hours, unit="h") + pd.to_timedelta(seconds, unit="s")


def build_order_lines(order_dates, products):
    """Create the order lines: which products, how many, at what discount."""
    items_per_order = rng.choice([1, 2, 3, 4], N_ORDERS, p=[0.58, 0.26, 0.11, 0.05])
    order_index = np.repeat(np.arange(N_ORDERS), items_per_order)
    line_month = order_dates.month.to_numpy()[order_index]
    n_lines = len(order_index)

    # category choice: Electronics and Fashion get a boost in the festive months
    category_index = np.zeros(n_lines, dtype=int)
    for month in range(1, 13):
        probs = np.array(CATEGORY_LINE_PROBS)
        if month in FESTIVE_MONTHS:
            probs[[0, 1]] *= 1.35
        in_month = line_month == month
        category_index[in_month] = rng.choice(len(CATEGORIES), in_month.sum(), p=probs / probs.sum())

    product_index = np.zeros(n_lines, dtype=int)
    for i, category in enumerate(CATEGORIES):
        pool = np.where(products["category"] == category)[0]
        popularity = products["popularity"].to_numpy()[pool]
        in_category = category_index == i
        product_index[in_category] = rng.choice(pool, in_category.sum(), p=popularity / popularity.sum())

    discount_probs = np.array(DISCOUNT_PROBS, dtype=float)[category_index]
    discount_probs[np.isin(line_month, FESTIVE_MONTHS)] *= FESTIVE_DISCOUNT_BOOST
    discount = DISCOUNT_LEVELS[sample_from_table(discount_probs, np.arange(n_lines))]

    quantity = sample_from_table(QUANTITY_PROBS, category_index) + 1
    bigger_basket = (discount >= 0.20) & (category_index != 0) & (rng.random(n_lines) < 0.25)
    quantity = quantity + bigger_basket

    price_factor = rng.choice([1.0, 0.95, 1.05], n_lines, p=[0.8, 0.1, 0.1])
    lines = pd.DataFrame({
        "order_index": order_index,
        "product_index": product_index,
        "quantity": quantity,
        "unit_price": (products["unit_price"].to_numpy()[product_index] * price_factor).round(2),
        "discount": discount,
        "category": np.array(CATEGORIES)[category_index],
    })
    return lines


def assign_status_and_delivery(order_dates, payment, ship_zone, lines):
    """Order status, delivery date and delivery days for every order."""
    has_fashion = np.bincount(lines.loc[lines["category"] == "Fashion", "order_index"], minlength=N_ORDERS) > 0
    has_electronics = np.bincount(lines.loc[lines["category"] == "Electronics", "order_index"], minlength=N_ORDERS) > 0

    cancel_prob = np.where(payment == "Cash on Delivery", 0.08, 0.03)
    return_prob = 0.03 + 0.04 * has_fashion + 0.015 * has_electronics
    cancelled = rng.random(N_ORDERS) < cancel_prob
    returned = ~cancelled & (rng.random(N_ORDERS) < return_prob)

    base_days = pd.Series(ship_zone).map({"metro": 2, "tier2": 3, "remote": 5}).to_numpy()
    extra_days = rng.poisson(pd.Series(ship_zone).map({"metro": 1.0, "tier2": 1.5, "remote": 2.0}).to_numpy())
    festive = np.isin(order_dates.month.to_numpy(), FESTIVE_MONTHS)
    festive_delay = np.where(festive, 1 + rng.poisson(0.7, N_ORDERS), 0)
    rare_delay = np.where(rng.random(N_ORDERS) < 0.02, rng.integers(4, 9, N_ORDERS), 0)
    delivery_days = np.clip(base_days + extra_days + festive_delay + rare_delay, 1, 20)

    order_day = order_dates.normalize()
    delivery_date = order_day + pd.to_timedelta(delivery_days, unit="D")
    status = np.where(cancelled, "Cancelled", np.where(returned, "Returned", "Delivered")).astype(object)

    not_delivered_yet = ~cancelled & (delivery_date > END_DATE)
    shipped = not_delivered_yet & (order_day < END_DATE)
    status[shipped] = "Shipped"
    status[not_delivered_yet & ~shipped] = "Processing"

    has_delivery = np.isin(status, ["Delivered", "Returned"])
    delivery_date = pd.Series(delivery_date).where(has_delivery)
    return status, delivery_date, delivery_days


def generate_orders(customers, products):
    # every customer gets at least one order, the rest follow customer activity
    activity = rng.lognormal(0, 0.9, N_CUSTOMERS) * customers["customer_segment"].map(SEGMENT_ACTIVITY).to_numpy()
    extra_orders = rng.choice(N_CUSTOMERS, N_ORDERS - N_CUSTOMERS, p=activity / activity.sum())
    order_customer_index = np.concatenate([np.arange(N_CUSTOMERS), extra_orders])

    order_dates = pd.DatetimeIndex(pick_order_dates(customers, order_customer_index))
    sort_order = np.argsort(order_dates.to_numpy(), kind="stable")
    order_customer_index = order_customer_index[sort_order]
    order_dates = order_dates[sort_order]

    # shipping address: usually the customer's own city, sometimes a gift to somewhere else
    own_location = customers["location_index"].to_numpy()[order_customer_index]
    other_location = rng.choice(len(locations), N_ORDERS, p=location_probs)
    ship_location = np.where(rng.random(N_ORDERS) < 0.92, own_location, other_location)
    payment = rng.choice(PAYMENT_METHODS, N_ORDERS, p=PAYMENT_PROBS)

    lines = build_order_lines(order_dates, products)
    status, delivery_date, delivery_days = assign_status_and_delivery(
        order_dates, payment, locations["zone"].to_numpy()[ship_location], lines)

    orders = pd.DataFrame({
        "order_id": [f"O{i:06d}" for i in range(1, N_ORDERS + 1)],
        "customer_id": customers["customer_id"].to_numpy()[order_customer_index],
        "order_date": order_dates,
        "order_status": status,
        "payment_method": payment,
        "shipping_city": locations["city"].to_numpy()[ship_location],
        "shipping_state": locations["state"].to_numpy()[ship_location],
        "delivery_date": delivery_date.to_numpy(),
    })

    # the same product can be picked twice for one order: merge those lines
    lines = lines.groupby(["order_index", "product_index"], as_index=False).agg(
        quantity=("quantity", "sum"), unit_price=("unit_price", "first"), discount=("discount", "first"))
    order_items = pd.DataFrame({
        "order_id": orders["order_id"].to_numpy()[lines["order_index"]],
        "product_id": products["product_id"].to_numpy()[lines["product_index"]],
        "quantity": lines["quantity"], "unit_price": lines["unit_price"], "discount": lines["discount"],
    })
    return orders, order_items, delivery_days


def generate_reviews(orders, order_items, products, delivery_days):
    """About a third of delivered order lines get a review."""
    delivered = orders[orders["order_status"] == "Delivered"][["order_id", "customer_id", "delivery_date"]].copy()
    delivered["delivery_days"] = delivery_days[delivered.index]
    lines = order_items.merge(delivered, on="order_id")
    lines = lines[rng.random(len(lines)) < 0.32].copy()
    lines = lines.merge(products[["product_id", "quality"]], on="product_id")

    late_penalty = 0.12 * np.maximum(0, lines["delivery_days"] - 5)
    score = lines["quality"] + rng.normal(0, 0.9, len(lines)) - late_penalty
    rating = np.clip(np.round(score), 1, 5).astype(int)

    review_text = [rng.choice(REVIEW_TEXT[r]) for r in rating]
    no_text = rng.random(len(lines)) < 0.25
    reviews = pd.DataFrame({
        "order_id": lines["order_id"], "customer_id": lines["customer_id"], "product_id": lines["product_id"],
        "rating": rating,
        "review_date": lines["delivery_date"] + pd.to_timedelta(rng.integers(1, 15, len(lines)), unit="D"),
        "review_text": np.where(no_text, None, review_text),
    })
    reviews = reviews.sort_values("review_date").reset_index(drop=True)
    reviews.insert(0, "review_id", [f"R{i:06d}" for i in range(1, len(reviews) + 1)])
    return reviews


# ---------------------------------------------------------------------------
# Data-quality problems added on purpose (small amounts)
# ---------------------------------------------------------------------------
def pick_rows(df, share):
    return rng.choice(df.index.to_numpy(), size=int(len(df) * share), replace=False)


def add_duplicates(df, share):
    return pd.concat([df, df.loc[pick_rows(df, share)]], ignore_index=True)


def mess_up_customers(customers):
    customers = customers.copy()
    customers["signup_date"] = customers["signup_date"].dt.strftime("%Y-%m-%d")
    customers.loc[pick_rows(customers, 0.04), "city"] = customers["city"].str.upper()
    customers.loc[pick_rows(customers, 0.03), "city"] = customers["city"].str.lower()
    customers.loc[pick_rows(customers, 0.02), "state"] = customers["state"].str.upper()
    customers.loc[pick_rows(customers, 0.01), "city"] = customers["city"] + " "
    customers.loc[customers["city"] == "Bengaluru", "city"] = np.where(
        rng.random((customers["city"] == "Bengaluru").sum()) < 0.05, "Bangalore", "Bengaluru")
    customers.loc[pick_rows(customers, 0.01), "customer_segment"] = customers["customer_segment"].str.lower()
    customers.loc[pick_rows(customers, 0.015), "email"] = np.nan
    customers.loc[pick_rows(customers, 0.005), "customer_segment"] = np.nan
    customers.loc[pick_rows(customers, 0.003), "signup_date"] = "2031-05-14"     # impossible date

    duplicates = customers.loc[pick_rows(customers, 0.01)].copy()
    half = duplicates.index[: len(duplicates) // 2]
    duplicates.loc[half, "customer_name"] = duplicates.loc[half, "customer_name"].str.upper()
    return pd.concat([customers, duplicates], ignore_index=True)


def mess_up_products(products):
    products = products.copy()
    variants = {"Electronics": ["electronics", "Electronic"], "Fashion": ["fashion", "FASHION"],
                "Home & Kitchen": ["Home and Kitchen", "home & kitchen"], "Grocery": ["grocery", "Groceries"],
                "Beauty & Personal Care": ["Beauty", "beauty & personal care"], "Books": ["books", "BOOKS"],
                "Sports & Fitness": ["Sports", "sports and fitness"], "Toys & Games": ["Toys", "toys & games"]}
    for row in pick_rows(products, 0.06):
        products.loc[row, "category"] = rng.choice(variants[products.loc[row, "category"]])
    products.loc[pick_rows(products, 0.004), "cost_price"] = np.nan
    return add_duplicates(products, 0.003)


def mess_up_orders(orders):
    orders = orders.copy()
    delivery_date = orders["delivery_date"]
    orders["order_date"] = orders["order_date"].dt.strftime("%Y-%m-%d %H:%M:%S")
    orders["delivery_date"] = delivery_date.dt.strftime("%Y-%m-%d")

    orders.loc[pick_rows(orders, 0.03), "order_status"] = orders["order_status"].str.lower()
    orders.loc[pick_rows(orders, 0.015), "order_status"] = orders["order_status"].str.upper()
    orders.loc[pick_rows(orders, 0.01), "order_status"] = orders["order_status"] + " "
    payment_variants = {"UPI": "upi", "Credit Card": "credit card", "Cash on Delivery": "COD", "Net Banking": "netbanking"}
    for clean_name, messy_name in payment_variants.items():
        rows = orders.index[orders["payment_method"] == clean_name]
        orders.loc[rng.choice(rows, int(len(rows) * 0.03), replace=False), "payment_method"] = messy_name
    orders.loc[pick_rows(orders, 0.03), "shipping_city"] = orders["shipping_city"].str.upper()
    orders.loc[pick_rows(orders, 0.005), "shipping_state"] = np.nan

    delivered_rows = orders.index[orders["order_status"].str.strip().str.lower() == "delivered"]
    orders.loc[rng.choice(delivered_rows, int(len(delivered_rows) * 0.005), replace=False), "delivery_date"] = np.nan
    has_date = orders.index[orders["delivery_date"].notna()]
    wrong_rows = rng.choice(has_date, int(len(has_date) * 0.003), replace=False)
    orders.loc[wrong_rows, "delivery_date"] = (
        pd.to_datetime(orders.loc[wrong_rows, "order_date"]) - pd.Timedelta(days=2)).dt.strftime("%Y-%m-%d")

    bad_rows = rng.choice(orders.index, 100, replace=False)       # broken timestamps
    orders.loc[bad_rows, "order_date"] = rng.choice(["2025-02-30 14:22:10", "0000-00-00 00:00:00", "2025-13-05 09:10:00"], 100)
    return add_duplicates(orders, 0.003)


def mess_up_order_items(order_items):
    order_items = order_items.copy()
    order_items.loc[pick_rows(order_items, 0.005), "discount"] = np.nan
    percent_rows = pick_rows(order_items, 0.002)
    order_items.loc[percent_rows, "discount"] = (order_items.loc[percent_rows, "discount"] * 100).round(0)
    order_items.loc[pick_rows(order_items, 0.001), "quantity"] = rng.choice([0, -1], int(len(order_items) * 0.001))
    order_items.loc[pick_rows(order_items, 0.003), "unit_price"] = np.nan
    return add_duplicates(order_items, 0.002)


def mess_up_reviews(reviews):
    reviews = reviews.copy()
    reviews["review_date"] = reviews["review_date"].dt.strftime("%Y-%m-%d")
    bad_rows = pick_rows(reviews, 0.01)
    reviews.loc[bad_rows, "rating"] = rng.choice([0, 6, 7, 10, -1], len(bad_rows))
    return add_duplicates(reviews, 0.003)


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    products = generate_products()
    customers = generate_customers()
    orders, order_items, delivery_days = generate_orders(customers, products)
    reviews = generate_reviews(orders, order_items, products, delivery_days)

    tables = {
        "customers": mess_up_customers(customers.drop(columns="location_index")),
        "products": mess_up_products(products.drop(columns=["popularity", "quality"])),
        "orders": mess_up_orders(orders),
        "order_items": mess_up_order_items(order_items),
        "reviews": mess_up_reviews(reviews),
    }
    for name, table in tables.items():
        table.to_csv(RAW_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: {len(table):,} rows")


if __name__ == "__main__":
    main()
