import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.database.connection import SessionLocal, init_db
from backend.database.models import (
    Category, Book, BookImage, MediaContent, book_categories,
    PodcastEpisode, VideoPlaylist, PlaylistVideo, CricfyMatch,
)
from datetime import datetime, timezone, date

COVER_COLORS = ["1e40af","059669","d97706","dc2626","7c3aed","db2777","0891b2","4f46e5"]

def seed():
    init_db()
    db = SessionLocal()
    try:
        if db.query(Category).count() > 0:
            print("Database already seeded. Skipping.")
            return

        categories_data = [
            ("Self-Help", "self-help", "Personal growth & productivity", "🧠", [
                ("Motivation", "motivation", "Inspiration & drive", "🔥"),
                ("Habits", "habits", "Building better routines", "🔄"),
                ("Mindfulness", "mindfulness", "Meditation & awareness", "🧘"),
            ]),
            ("Business", "business", "Entrepreneurship & management", "💼", [
                ("Entrepreneurship", "entrepreneurship", "Startups & ventures", "🚀"),
                ("Management", "management", "Leadership & teams", "👔"),
                ("Marketing", "marketing", "Brands & growth", "📢"),
            ]),
            ("Psychology", "psychology", "Mind & behavior", "🧪", [
                ("Cognitive Science", "cognitive-science", "Thinking & perception", "🧠"),
                ("Behavioral", "behavioral", "Human behavior", "📊"),
            ]),
            ("Philosophy", "philosophy", "Life & wisdom", "🤔", [
                ("Eastern Philosophy", "eastern-philosophy", "Zen & Tao", "☯️"),
                ("Western Philosophy", "western-philosophy", "Logic & ethics", "🏛️"),
            ]),
            ("Finance", "finance", "Money & investing", "💰", [
                ("Personal Finance", "personal-finance", "Budgeting & saving", "🏦"),
                ("Investing", "investing", "Stocks & markets", "📈"),
                ("Real Estate", "real-estate", "Property & wealth", "🏠"),
            ]),
            ("Productivity", "productivity", "Efficiency & habits", "⚡", [
                ("Time Management", "time-management", "Getting things done", "⏰"),
                ("Focus", "focus", "Deep work & attention", "🎯"),
            ]),
            ("History", "history", "Past & civilizations", "📜", [
                ("World History", "world-history", "Global events", "🌍"),
                ("Biographies", "biographies", "Lives of great people", "👤"),
            ]),
            ("Fiction", "fiction", "Novels & storytelling", "📖", [
                ("Classic Literature", "classic-literature", "Timeless works", "📚"),
                ("Science Fiction", "science-fiction", "Future & fantasy", "🚀"),
                ("Mystery", "mystery", "Crime & detection", "🔍"),
            ]),
            ("Science", "science", "Discovery & innovation", "🔬", [
                ("Physics", "physics", "Laws of nature", "⚛️"),
                ("Biology", "biology", "Life sciences", "🧬"),
                ("Astronomy", "astronomy", "Space & cosmos", "🌌"),
            ]),
            ("Technology", "technology", "Digital age & AI", "💻", [
                ("AI & Machine Learning", "ai-ml", "Artificial intelligence", "🤖"),
                ("Programming", "programming", "Code & development", "💾"),
                ("Cybersecurity", "cybersecurity", "Digital protection", "🔒"),
            ]),
            ("Electronics", "electronics", "Gadgets, devices & accessories", "📱", [
                ("Smartphones", "smartphones", "Phones & phablets", "📱"),
                ("Laptops", "laptops", "Notebooks & ultrabooks", "💻"),
                ("Audio", "audio", "Headphones & speakers", "🎧"),
                ("Wearables", "wearables", "Smartwatches & bands", "⌚"),
                ("Cameras", "cameras", "Photography & video", "📷"),
            ]),
            ("Clothing", "clothing", "Fashion & apparel for all", "👕", [
                ("Men's Wear", "mens-wear", "Shirts, pants & suits", "👔"),
                ("Women's Wear", "womens-wear", "Dresses, tops & skirts", "👗"),
                ("Footwear", "footwear", "Shoes, sneakers & boots", "👟"),
                ("Sportswear", "sportswear", "Athletic & gym wear", "🏃"),
                ("Accessories", "accessories", "Bags, belts & jewelry", "👜"),
            ]),
        ]
        parent_map = {}
        for name, slug, desc, icon, subs in categories_data:
            parent = Category(name=name, slug=slug, description=desc, icon=icon)
            db.add(parent)
            db.flush()
            parent_map[name] = parent
            for sub_name, sub_slug, sub_desc, sub_icon in subs:
                sub = Category(name=sub_name, slug=sub_slug, description=sub_desc, icon=sub_icon, parent_id=parent.id)
                db.add(sub)
        db.flush()

        category_map = {c.name: c for c in db.query(Category).all()}

        book_meta = [
            ("Atomic Habits", "James Clear", ["Habits","Motivation"], 14.99, "An Easy & Proven Way to Build Good Habits & Break Bad Ones", "Avery", 2018, 320),
            ("The Lean Startup", "Eric Ries", ["Entrepreneurship","AI & Machine Learning"], 18.99, "How Today's Entrepreneurs Use Continuous Innovation", "Crown Business", 2011, 336),
            ("Deep Work", "Cal Newport", ["Focus","Time Management"], 15.99, "Rules for Focused Success in a Distracted World", "Grand Central", 2016, 296),
            ("Think and Grow Rich", "Napoleon Hill", ["Motivation","Personal Finance"], 12.99, "The Landmark Bestseller", "TarcherPerigee", 1937, 320),
            ("The 7 Habits of Highly Effective People", "Stephen R. Covey", ["Habits","Management"], 16.99, "Powerful Lessons in Personal Change", "Free Press", 1989, 384),
            ("How to Win Friends and Influence People", "Dale Carnegie", ["Motivation","Management"], 13.99, "The Only Book You Need to Lead You to Success", "Pocket Books", 1936, 288),
            ("Sapiens", "Yuval Noah Harari", ["World History","Biographies"], 19.99, "A Brief History of Humankind", "Harper", 2015, 464),
            ("The Psychology of Money", "Morgan Housel", ["Personal Finance","Behavioral"], 14.99, "Timeless Lessons on Wealth, Greed, and Happiness", "Harriman House", 2020, 256),
            ("Rich Dad Poor Dad", "Robert Kiyosaki", ["Personal Finance","Investing"], 11.99, "What the Rich Teach Their Kids About Money", "Plata", 1997, 336),
            ("The Alchemist", "Paulo Coelho", ["Classic Literature","Eastern Philosophy"], 13.99, "A Fable About Following Your Dream", "HarperOne", 1988, 208),
            ("Zero to One", "Peter Thiel", ["Entrepreneurship","AI & Machine Learning"], 16.99, "Notes on Startups, or How to Build the Future", "Crown Business", 2014, 256),
            ("The Power of Habit", "Charles Duhigg", ["Habits","Behavioral"], 15.99, "Why We Do What We Do in Life and Business", "Random House", 2012, 400),
            ("Thinking, Fast and Slow", "Daniel Kahneman", ["Cognitive Science","Behavioral"], 18.99, "The #1 New York Times Bestseller", "FSG", 2011, 512),
            ("Start with Why", "Simon Sinek", ["Management","Motivation"], 14.99, "How Great Leaders Inspire Everyone to Take Action", "Portfolio", 2009, 256),
            ("Good to Great", "Jim Collins", ["Management","Entrepreneurship"], 17.99, "Why Some Companies Make the Leap", "HarperBusiness", 2001, 300),
            ("The 4-Hour Work Week", "Tim Ferriss", ["Time Management","Entrepreneurship"], 15.99, "Escape the 9-5, Live Anywhere", "Crown", 2007, 416),
            ("Man's Search for Meaning", "Viktor Frankl", ["Western Philosophy","Cognitive Science"], 12.99, "A Young Psychologist's Account of Life", "Beacon Press", 1946, 200),
            ("Daring Greatly", "Brené Brown", ["Mindfulness","Behavioral"], 14.99, "How the Courage to Be Vulnerable Transforms", "Gotham", 2012, 304),
            ("The Art of War", "Sun Tzu", ["Eastern Philosophy","Management"], 9.99, "The Classic Guide to Strategy", "Shambhala", 500, 240),
            ("The Compound Effect", "Darren Hardy", ["Habits","Motivation"], 12.99, "Jumpstart Your Income, Your Life", "Momentum Media", 2010, 176),
            ("Meditations", "Marcus Aurelius", ["Western Philosophy","Motivation"], 11.99, "Timeless wisdom from a Roman emperor", "Penguin", 180, 304),
            ("The Design of Everyday Things", "Don Norman", ["Cognitive Science","Programming"], 16.99, "Why some products satisfy customers", "Basic Books", 2013, 368),
            ("Hooked", "Nir Eyal", ["Marketing","Entrepreneurship"], 14.99, "How to Build Habit-Forming Products", "Portfolio", 2014, 256),
            ("The Hard Thing About Hard Things", "Ben Horowitz", ["Entrepreneurship","Management"], 17.99, "Building a Business When There Are No Easy Answers", "HarperBusiness", 2014, 304),
            ("Measure What Matters", "John Doerr", ["Management","Entrepreneurship"], 16.99, "How Google, Bono, and the Gates Foundation Rock the World with OKRs", "Portfolio", 2018, 320),
            ("The Mom Test", "Rob Fitzpatrick", ["Entrepreneurship","Marketing"], 13.99, "How to talk to customers & learn if your business is a good idea", "CreateSpace", 2013, 144),
            ("Never Split the Difference", "Chris Voss", ["Motivation","Management"], 15.99, "Negotiating As If Your Life Depended On It", "HarperBusiness", 2016, 288),
            ("Factfulness", "Hans Rosling", ["World History","Science"], 18.99, "Ten Reasons We're Wrong About the World", "Flatiron Books", 2018, 352),
            ("A Brief History of Time", "Stephen Hawking", ["Physics","Astronomy"], 16.99, "From the Big Bang to Black Holes", "Bantam", 1988, 256),
            ("The Selfish Gene", "Richard Dawkins", ["Biology","Cognitive Science"], 15.99, "Evolutionary biology classic", "Oxford UP", 1976, 384),
            ("Cosmos", "Carl Sagan", ["Astronomy","Science"], 19.99, "A Personal Voyage through space and time", "Ballantine", 1980, 384),
            ("1984", "George Orwell", ["Classic Literature","Science Fiction"], 12.99, "Dystopian social science fiction novel", "Secker & Warburg", 1949, 328),
            ("Brave New World", "Aldous Huxley", ["Science Fiction","Classic Literature"], 13.99, "A dystopian novel set in a futuristic World State", "Chatto & Windus", 1932, 288),
            ("To Kill a Mockingbird", "Harper Lee", ["Classic Literature","Mystery"], 14.99, "A novel about racial injustice in the Deep South", "J.B. Lippincott", 1960, 336),
            ("The Great Gatsby", "F. Scott Fitzgerald", ["Classic Literature","Mystery"], 11.99, "A story of the mysteriously wealthy Jay Gatsby", "Scribner", 1925, 180),
            ("The Catcher in the Rye", "J.D. Salinger", ["Classic Literature","Psychology"], 13.99, "Story of Holden Caulfield's experiences in New York City", "Little, Brown", 1951, 234),
            ("Dune", "Frank Herbert", ["Science Fiction","Classic Literature"], 18.99, "Set in the distant future, a complex story of politics, religion, and ecology", "Chilton Books", 1965, 688),
            ("The Hobbit", "J.R.R. Tolkien", ["Classic Literature","Science Fiction"], 16.99, "Bilbo Baggins embarks on an unexpected journey", "George Allen & Unwin", 1937, 310),
            ("The Great Mental Models Vol 1", "Shane Parrish", ["Focus","Cognitive Science"], 17.99, "General thinking concepts", "Portfolio", 2019, 304),
            ("The Infinite Game", "Simon Sinek", ["Management","Motivation"], 15.99, "Leadership with an infinite mindset", "Portfolio", 2019, 272),
            ("Range", "David Epstein", ["Focus","Behavioral"], 16.99, "Why Generalists Triumph in a Specialized World", "Riverhead", 2019, 352),
            ("The Subtle Art of Not Giving a F*ck", "Mark Manson", ["Motivation","Mindfulness"], 14.99, "A Counterintuitive Approach to Living a Good Life", "HarperOne", 2016, 224),
            ("Principles", "Ray Dalio", ["Investing","Management"], 21.99, "Life and Work Principles from the Bridgewater founder", "Simon & Schuster", 2017, 592),
            ("Educated", "Tara Westover", ["Biographies","Motivation"], 15.99, "A memoir of a woman who grows up in a survivalist family", "Random House", 2018, 352),
            ("Becoming", "Michelle Obama", ["Biographies","Motivation"], 19.99, "Former First Lady Michelle Obama's memoir", "Crown", 2018, 448),
        ]

        electronics_meta = [
            ("iPhone 15 Pro Max", "Apple", ["Smartphones"], 1199.00, "6.7-inch OLED, A17 Pro chip, 48MP camera", {"color":"Natural Titanium","storage":"256GB","ram":"8GB","battery":"4422mAh","display":"6.7\" Super Retina XDR","chip":"A17 Pro"}),
            ("Samsung Galaxy S24 Ultra", "Samsung", ["Smartphones"], 1099.00, "6.8-inch Dynamic AMOLED, Snapdragon 8 Gen 3", {"color":"Titanium Gray","storage":"256GB","ram":"12GB","battery":"5000mAh","display":"6.8\" Dynamic AMOLED 2X","chip":"Snapdragon 8 Gen 3"}),
            ("Google Pixel 8 Pro", "Google", ["Smartphones"], 899.00, "6.7-inch LTPO OLED, Tensor G3 chip", {"color":"Obsidian","storage":"128GB","ram":"12GB","battery":"5050mAh","display":"6.7\" LTPO OLED","chip":"Tensor G3"}),
            ("OnePlus 12", "OnePlus", ["Smartphones"], 799.00, "6.82-inch ProXDR Display, Snapdragon 8 Gen 3", {"color":"Flowy Emerald","storage":"256GB","ram":"16GB","battery":"5400mAh","display":"6.82\" ProXDR","chip":"Snapdragon 8 Gen 3"}),
            ("MacBook Pro 16 M3 Max", "Apple", ["Laptops"], 3499.00, "16-inch Liquid Retina XDR, M3 Max chip", {"color":"Space Black","storage":"1TB","ram":"36GB","display":"16.2\" Liquid Retina XDR","chip":"M3 Max","battery":"22 hours"}),
            ("Dell XPS 15", "Dell", ["Laptops"], 2199.00, "15.6-inch 3.5K OLED, Intel Core i9-13900H", {"color":"Platinum Silver","storage":"1TB SSD","ram":"32GB","display":"15.6\" 3.5K OLED","cpu":"Intel i9-13900H","battery":"86Wh"}),
            ("ASUS ROG Zephyrus G14", "ASUS", ["Laptops"], 1599.00, "14-inch QHD 165Hz, AMD Ryzen 9 7940HS", {"color":"Moonlight White","storage":"1TB SSD","ram":"16GB","display":"14\" QHD 165Hz","cpu":"AMD Ryzen 9 7940HS","gpu":"NVIDIA RTX 4060"}),
            ("Lenovo ThinkPad X1 Carbon Gen 11", "Lenovo", ["Laptops"], 1849.00, "14-inch WUXGA, Intel Core i7-1365U", {"color":"Black","storage":"512GB SSD","ram":"16GB","display":"14\" WUXGA IPS","cpu":"Intel i7-1365U","battery":"57Wh"}),
            ("Sony WH-1000XM5", "Sony", ["Audio"], 349.00, "Industry-leading noise cancellation wireless headphones", {"color":"Black","type":"Over-ear","battery":"30 hours","noise_cancelling":"Yes","connectivity":"Bluetooth 5.2","weight":"250g"}),
            ("AirPods Pro 2", "Apple", ["Audio"], 249.00, "Active Noise Cancellation with Transparency mode", {"color":"White","type":"In-ear","battery":"6 hours","chip":"H2","connectivity":"Bluetooth 5.3","water_resistant":"IPX4"}),
            ("Bose QuietComfort Ultra", "Bose", ["Audio"], 429.00, "Immersive audio with spatial sound", {"color":"Triple Black","type":"Over-ear","battery":"24 hours","noise_cancelling":"Yes","connectivity":"Bluetooth 5.3","weight":"252g"}),
            ("Samsung Galaxy Buds3 Pro", "Samsung", ["Audio"], 199.99, "Intelligent noise cancelling earbuds", {"color":"Silver","type":"In-ear","battery":"6 hours","noise_cancelling":"Yes","connectivity":"Bluetooth 5.4","water_resistant":"IP57"}),
            ("Apple Watch Ultra 2", "Apple", ["Wearables"], 799.00, "49mm titanium case, precision dual-frequency GPS", {"color":"Natural Titanium","case_size":"49mm","battery":"36 hours","display":"410x502 OLED","chip":"S9 SiP","water_resistant":"WR100"}),
            ("Samsung Galaxy Watch6 Classic", "Samsung", ["Wearables"], 399.00, "47mm rotating bezel smartwatch", {"color":"Black","case_size":"47mm","battery":"425mAh","display":"1.47\" Super AMOLED","chip":"Exynos W930","water_resistant":"5ATM"}),
            ("Fitbit Charge 6", "Google/Fitbit", ["Wearables"], 159.95, "Advanced fitness tracker with built-in GPS", {"color":"Black","type":"Fitness band","battery":"7 days","display":"AMOLED","sensors":"Heart rate, SpO2, GPS","water_resistant":"50m"}),
            ("Garmin Forerunner 265", "Garmin", ["Wearables"], 449.99, "Running smartwatch with AMOLED display", {"color":"Black","case_size":"46mm","battery":"13 days","display":"1.3\" AMOLED","gps":"Multi-band GNSS","water_resistant":"5ATM"}),
            ("Sony A7 IV", "Sony", ["Cameras"], 2499.99, "33MP full-frame mirrorless camera", {"color":"Black","sensor":"33MP Full-Frame","iso":"100-51200","video":"4K 60fps","stabilization":"5-axis IBIS","weight":"658g"}),
            ("Canon EOS R6 Mark II", "Canon", ["Cameras"], 2499.00, "24.2MP full-frame mirrorless camera", {"color":"Black","sensor":"24.2MP Full-Frame","iso":"100-102400","video":"4K 60fps","stabilization":"5-axis IBIS","weight":"670g"}),
            ("DJI Osmo Pocket 3", "DJI", ["Cameras"], 519.00, "1-inch CMOS gimbal camera, 4K 120fps", {"color":"Black","sensor":"1-inch CMOS","video":"4K 120fps","gimbal":"3-axis","display":"2-inch rotatable touchscreen","weight":"179g"}),
            ("GoPro Hero 12 Black", "GoPro", ["Cameras"], 399.99, "5.3K action camera with HyperSmooth 6.0", {"color":"Black","sensor":"1/1.9-inch","video":"5.3K 60fps","stabilization":"HyperSmooth 6.0","waterproof":"10m","weight":"154g"}),
            ("iPad Pro 12.9 M2", "Apple", ["Laptops"], 1099.00, "12.9-inch Liquid Retina XDR, M2 chip", {"color":"Space Gray","storage":"256GB","ram":"8GB","display":"12.9\" Liquid Retina XDR","chip":"M2","battery":"10 hours"}),
            ("Microsoft Surface Pro 10", "Microsoft", ["Laptops"], 1499.99, "13-inch PixelSense Flow, Intel Core Ultra 7", {"color":"Platinum","storage":"512GB SSD","ram":"16GB","display":"13\" PixelSense Flow","cpu":"Intel Core Ultra 7","battery":"16 hours"}),
            ("Sennheiser Momentum 4", "Sennheiser", ["Audio"], 349.95, "High-fidelity wireless headphones", {"color":"White","type":"Over-ear","battery":"60 hours","noise_cancelling":"Adaptive","connectivity":"Bluetooth 5.2","codec":"aptX Adaptive"}),
            ("Nothing Ear (2)", "Nothing", ["Audio"], 149.00, "Transparent design earbuds with ANC", {"color":"White","type":"In-ear","battery":"6 hours","noise_cancelling":"Yes","connectivity":"Bluetooth 5.3","water_resistant":"IP54"}),
            ("Samsung Galaxy Tab S9 Ultra", "Samsung", ["Laptops"], 1199.99, "14.6-inch Dynamic AMOLED 2X, Snapdragon 8 Gen 2", {"color":"Graphite","storage":"256GB","ram":"12GB","display":"14.6\" AMOLED","chip":"Snapdragon 8 Gen 2","battery":"11200mAh"}),
            ("Ray-Ban Meta Smart Glasses", "Meta/Ray-Ban", ["Wearables"], 299.00, "AI-powered smart glasses with camera", {"color":"Matte Black","type":"Smart glasses","camera":"12MP","audio":"Open-ear speakers","battery":"4 hours","weight":"49g"}),
            ("Fujifilm X-T5", "Fujifilm", ["Cameras"], 1699.00, "40MP APS-C mirrorless camera", {"color":"Silver","sensor":"40MP X-Trans CMOS","iso":"125-12800","video":"6.2K 30fps","stabilization":"7-stop IBIS","weight":"557g"}),
            ("Google Pixel Watch 2", "Google", ["Wearables"], 349.99, "41mm smartwatch with Fitbit integration", {"color":"Matte Black","case_size":"41mm","battery":"24 hours","display":"1.2\" AMOLED","chip":"Qualcomm SW5100","water_resistant":"5ATM"}),
            ("SteelSeries Arctis Nova Pro", "SteelSeries", ["Audio"], 349.99, "Premium gaming headset with ANC", {"color":"Black","type":"Over-ear","battery":"36 hours","noise_cancelling":"Yes","connectivity":"2.4GHz + Bluetooth","frequency":"20-22000Hz"}),
            ("MacBook Air 15 M3", "Apple", ["Laptops"], 1299.00, "15.3-inch Liquid Retina, M3 chip", {"color":"Midnight","storage":"256GB","ram":"8GB","display":"15.3\" Liquid Retina","chip":"M3","battery":"18 hours"}),
        ]

        clothing_meta = [
            ("Classic Fit Oxford Shirt", "Ralph Lauren", ["Men's Wear"], 99.50, "Timeless button-down Oxford shirt in premium cotton", {"material":"100% Cotton","fit":"Classic","size":"S-3XL","color":"White","care":"Machine washable","origin":"Imported"}),
            ("Slim Fit Chino Pants", "Dockers", ["Men's Wear"], 69.50, "Everyday Khaki chino with stretch comfort", {"material":"98% Cotton 2% Elastane","fit":"Slim","size":"28-42","color":"Khaki","care":"Machine wash","rise":"Mid-rise"}),
            ("Merino Wool Sweater", "Uniqlo", ["Men's Wear"], 49.90, "Lightweight merino wool crew neck sweater", {"material":"100% Merino Wool","fit":"Regular","size":"S-3XL","color":"Navy","care":"Dry clean recommended","weight":"Lightweight"}),
            ("Leather Bomber Jacket", "AllSaints", ["Men's Wear"], 495.00, "Genuine lambskin leather bomber jacket", {"material":"100% Lambskin Leather","fit":"Slim","size":"S-2XL","color":"Black","care":"Professional leather clean","lining":"Polyester"}),
            ("Linen Blend Blazer", "Hugo Boss", ["Men's Wear"], 395.00, "Lightweight linen blazer for warm weather", {"material":"55% Linen 45% Cotton","fit":"Regular","size":"38-54R","color":"Beige","care":"Dry clean","pockets":"3 patch pockets"}),
            ("Cashmere Overcoat", "Burberry", ["Men's Wear"], 1895.00, "Luxurious cashmere single-breasted overcoat", {"material":"100% Cashmere","fit":"Regular","size":"38-52R","color":"Charcoal","care":"Professional clean","length":"Knee-length"}),
            ("Printed Midi Dress", "Reformation", ["Women's Wear"], 198.00, "Eco-friendly viscose midi dress with botanical print", {"material":"Eco Viscose","fit":"Bodycon","size":"XS-XL","color":"Botanical Print","care":"Hand wash cold","length":"Midi"}),
            ("Tailored Wool Blazer", "Theory", ["Women's Wear"], 425.00, "Classic single-breasted wool blazer", {"material":"95% Wool 5% Elastane","fit":"Tailored","size":"0-14","color":"Camel","care":"Dry clean","lining":"Crepe de Chine"}),
            ("Silk Evening Gown", "Oscar de la Renta", ["Women's Wear"], 2590.00, "Floor-length silk gown with cowl neckline", {"material":"100% Silk","fit":"Fitted","size":"0-12","color":"Navy","care":"Dry clean","length":"Floor-length"}),
            ("Cashmere Wrap Cardigan", "Naked Cashmere", ["Women's Wear"], 295.00, "Ultra-soft cashmere wrap cardigan", {"material":"100% Cashmere","fit":"Relaxed","size":"XS-XL","color":"Heather Gray","care":"Hand wash","weight":"Mid-weight"}),
            ("High-Waist Trousers", "COS", ["Women's Wear"], 135.00, "Wide-leg high-waist trousers in crepe", {"material":"52% Viscose 48% Rayon","fit":"Wide","size":"2-14","color":"Black","care":"Machine wash","rise":"High-waist"}),
            ("Denim Jacket", "Levi's", ["Men's Wear","Women's Wear"], 98.00, "Classic trucker denim jacket", {"material":"100% Cotton Denim","fit":"Regular","size":"XS-3XL","color":"Medium Wash","care":"Machine wash","weight":"14 oz denim"}),
            ("Running Shoes Pro", "Nike", ["Footwear"], 179.99, "Advanced running shoes with ZoomX foam", {"material":"Mesh upper, rubber sole","size":"6-15","color":"Black/White","type":"Running","cushioning":"ZoomX","weight":"258g"}),
            ("Ultraboost 5", "Adidas", ["Footwear"], 159.99, "Ultra-comfortable running shoes with Boost midsole", {"material":"Primeknit upper, Continental sole","size":"6-15","color":"Core Black","type":"Running","cushioning":"Boost","weight":"299g"}),
            ("Chelsea Boots", "Blundstone", ["Footwear"], 210.00, "Classic pull-on Chelsea boots in premium leather", {"material":"Premium Leather","size":"5-14","color":"Brown","type":"Boots","sole":"TPU outsole","waterproof":"Yes"}),
            ("Leather Loafers", "Tod's", ["Footwear"], 595.00, "Handcrafted Italian leather driving shoes", {"material":"Calf Leather","size":"6-13","color":"Tan","type":"Loafers","sole":"Rubber pebbles","origin":"Italy"}),
            ("Trail Running Shoes", "Salomon", ["Footwear"], 139.99, "All-terrain trail running shoes with Contagrip", {"material":"Mesh/synthetic","size":"6-14","color":"Dark Grey","type":"Trail","cushioning":"Energy Foam","drop":"8mm"}),
            ("Dress Oxfords", "Allen Edmonds", ["Footwear"], 395.00, "Cap-toe oxford dress shoes crafted in USA", {"material":"Calfskin Leather","size":"7-15","color":"Walnut","type":"Oxfords","sole":"Leather with rubber","construction":"Goodyear welt"}),
            ("Dri-FIT Training Tee", "Nike", ["Sportswear"], 35.00, "Moisture-wicking training shirt with Dri-FIT", {"material":"100% Polyester","fit":"Standard","size":"S-3XL","color":"Black","care":"Machine wash","technology":"Dri-FIT"}),
            ("Yoga Leggings", "Lululemon", ["Sportswear"], 98.00, "High-rise align leggings with Nulu fabric", {"material":"Nulu (Nylon/Lycra)","fit":"Tight","size":"0-20","color":"Black","care":"Machine wash cold","rise":"High-rise"}),
            ("Performance Polo", "Under Armour", ["Sportswear"], 55.00, "UA Tech™ fabric polo for all-day comfort", {"material":"100% Polyester","fit":"Standard","size":"S-3XL","color":"Navy","care":"Machine wash","technology":"UA Tech™"}),
            ("Running Shorts 5-inch", "Lululemon", ["Sportswear"], 58.00, "Fast and Free high-intensity running shorts", {"material":"Nulon/Lycra","fit":"Slim","size":"XS-XL","color":"True Navy","care":"Machine wash","length":"5-inch inseam"}),
            ("Down Parka", "The North Face", ["Sportswear"], 299.00, "Waterproof 700-fill down parka for extreme cold", {"material":"700-Fill Down, DryVent shell","fit":"Regular","size":"S-3XL","color":"Black","care":"Machine wash","warmth":"-30°F rated"}),
            ("Cashmere Scarf", "Burberry", ["Accessories"], 390.00, "Iconic check cashmere scarf", {"material":"100% Cashmere","size":"168x30cm","color":"Nova Check","care":"Dry clean","weight":"Lightweight","origin":"Scotland"}),
            ("Leather Belt", "Hermès", ["Accessories"], 650.00, "Classic 32mm reversible leather belt", {"material":"Box Calf Leather","size":"70-120cm","color":"Black/Brown","buckle":"Silver palladium","width":"32mm","origin":"France"}),
            ("Gold Hoop Earrings", "Mejuri", ["Accessories"], 195.00, "14K gold filled medium hoops", {"material":"14K Gold Filled","size":"25mm diameter","color":"Yellow Gold","type":"Hoop","closure":"Leverback","hypoallergenic":"Yes"}),
            ("Silk Tie", "Hermès", ["Accessories"], 195.00, "Classic printed silk tie", {"material":"100% Silk","size":"150cm length","color":"Blue/Orange","pattern":"Printed","width":"8cm","origin":"France"}),
            ("Leather Tote Bag", "Cuyana", ["Accessories"], 275.00, "Minimalist leather tote with clean lines", {"material":"Italian Leather","size":"40x30x15cm","color":"Tan","hardware":"Gold","closure":"Magnetic","strap":"Dual top handles"}),
            ("Aviator Sunglasses", "Ray-Ban", ["Accessories"], 163.00, "Classic Aviator sunglasses with gradient lens", {"material":"Metal frame, glass lens","size":"55-58mm","color":"Gold/Green","lens":"Gradient","protection":"100% UV","polarized":"Available"}),
            ("Leather Wallet", "Bellroy", ["Accessories"], 89.00, "Slim leather wallet with RFID protection", {"material":"Premium Leather","size":"10x7cm","color":"Navy","slots":"8 card slots","rfid":"Protected","origin":"Australia"}),
        ]

        existing_books = {b.title: b for b in db.query(Book).all()}
        
        def make_book(title, author, cats, price, desc, pub, year, pages, ptype="book", brand=None, specs=None):
            if title in existing_books:
                book = existing_books[title]
            else:
                book = Book(title=title, author=author, total_chapters=pages//20 if pages else 10, price=price, stock_quantity=50, is_digital=False, product_type=ptype, brand=brand, specifications=specs or {})
                db.add(book)
                db.flush()
            book.description = desc
            book.author = author
            book.publisher = pub
            book.publication_year = year
            book.pages = pages
            book.price = price
            book.stock_quantity = 50
            book.is_digital = False
            book.is_active = True
            book.product_type = ptype
            book.brand = brand
            book.specifications = specs or {}
            return book

        all_products = []
        
        for meta in book_meta:
            name, author, cats, price, desc, pub, year, pages = meta
            b = make_book(name, author, cats, price, desc, pub, year, pages, "book")
            all_products.append((b, cats))
        
        for meta in electronics_meta:
            name, brand, cats, price, desc, specs = meta
            b = make_book(name, brand, cats, price, desc, brand, 2024, 1, "electronics", brand, specs)
            all_products.append((b, cats))
        
        for meta in clothing_meta:
            name, brand, cats, price, desc, specs = meta
            b = make_book(name, brand, cats, price, desc, brand, 2024, 1, "clothing", brand, specs)
            all_products.append((b, cats))
        
        db.flush()

        def add_cover(book, color_idx, label):
            color = COVER_COLORS[color_idx % len(COVER_COLORS)]
            cover_url = f"https://placehold.co/300x450/{color}/ffffff?text={label.replace(' ', '+')[:30]}"
            db.add(BookImage(book_id=book.id, url=cover_url, alt_text=f"{book.title} cover", is_primary=True))

        for i, (book, cats) in enumerate(all_products):
            add_cover(book, i, book.title)
            for cat_name in cats:
                if cat_name in category_map:
                    try:
                        db.execute(book_categories.insert().values(book_id=book.id, category_id=category_map[cat_name].id))
                    except:
                        pass
        
        db.flush()

        media_data = [
            ("Atomic Habits: The Power of 1%", "podcast", "youtube", "https://youtu.be/PZ7lDrwYdZc", "https://www.youtube.com/embed/PZ7lDrwYdZc", "James Clear", ["habits","productivity"], 1),
            ("Thinking, Fast and Slow Explained", "video", "youtube", "https://youtu.be/CjVQJirIrG0", "https://www.youtube.com/embed/CjVQJirIrG0", "Daniel Kahneman", ["psychology","thinking"], 1),
            ("Book Review: Deep Work by Cal Newport", "video", "instagram", "https://instagram.com/reel/xyz", None, "BookTok", ["deep work","focus"], 1),
            ("How to Build Good Habits", "video", "youtube", "https://youtu.be/example1", "https://www.youtube.com/embed/example1", "Better Ideas", ["habits","self-help"], 1),
            ("The Psychology of Money Summary", "podcast", "apple", "https://podcasts.apple.com/episode/xyz", None, "Morgan Housel", ["finance","money"], 1),
            ("Daily Reading: Chapter by Chapter", "video", "instagram", "https://instagram.com/reel/xyz2", None, "BooksDaily", ["reading","daily"], 0),
            ("Why You Should Read 'The Alchemist'", "video", "tiktok", "https://tiktok.com/@booktok/video/xyz2", None, "BookTok", ["alchemist","fiction"], 1),
            ("Rich Dad Poor Dad - Full Breakdown", "video", "youtube", "https://youtu.be/example2", "https://www.youtube.com/embed/example2", "Financial Education", ["finance","investing"], 1),
            ("iPhone 15 Pro Max Review", "video", "youtube", "https://youtu.be/iphone15", "https://www.youtube.com/embed/iphone15", "TechReviewer", ["iphone","apple"], 1),
            ("Samsung Galaxy S24 Ultra Hands-On", "video", "youtube", "https://youtu.be/s24u", "https://www.youtube.com/embed/s24u", "TechGuru", ["samsung","galaxy"], 1),
        ]
        book_map = {b.title: b for b in db.query(Book).all()}
        for title, mtype, platform, url, embed, author, tags, featured in media_data:
            book_id = None
            for bt, b in book_map.items():
                if title.lower().startswith(bt.split(":")[0].strip().lower()[:10]):
                    book_id = b.id
                    break
            db.add(MediaContent(book_id=book_id, title=title, media_type=mtype, platform=platform, url=url, embed_url=embed, author=author, tags=tags, is_featured=bool(featured), thumbnail_url=f"https://placehold.co/480x360/1e40af/ffffff?text={title.replace(' ','+')[:30]}", duration_minutes=15))

        podcast_data = [
            ("Atomic Habits Deep Dive", "James Clear & Book Club", "spotify", "https://open.spotify.com/episode/atomic1", None, 45, 1, 1, ["habits","atomic","productivity"], True),
            ("The Lean Startup Review", "Startup Podcast", "apple", "https://podcasts.apple.com/episode/lean1", None, 38, 1, 2, ["lean","startup","business"], True),
            ("Sapiens: A Brief History", "History Unfolded", "spotify", "https://open.spotify.com/episode/sapiens1", None, 52, 1, 3, ["history","sapiens","humankind"], True),
            ("Deep Work: Focus Rules", "Productivity Lab", "youtube", "https://youtu.be/podcast_deep1", "https://www.youtube.com/embed/podcast_deep1", 30, 1, 4, ["deep work","focus","productivity"], True),
            ("Psychology of Money Explained", "Finance Talks", "apple", "https://podcasts.apple.com/episode/money1", None, 42, 1, 5, ["money","psychology","finance"], True),
            ("Think and Grow Rich Analysis", "Success Stories", "spotify", "https://open.spotify.com/episode/think1", None, 55, 1, 6, ["success","wealth","mindset"], False),
            ("Power of Habit Breakdown", "Behavior Science", "youtube", "https://youtu.be/podcast_habit1", "https://www.youtube.com/embed/podcast_habit1", 35, 1, 7, ["habits","behavior","science"], True),
            ("Book Review Weekly Ep 42", "BooksDaily Podcast", "spotify", "https://open.spotify.com/show/booksdaily1", None, 60, None, None, ["books","review","weekly"], True),
            ("Author Interview: Best Sellers", "Lit Insights", "apple", "https://podcasts.apple.com/show/lit1", None, 48, None, None, ["interview","authors","bestsellers"], False),
            ("Reading Habits That Changed My Life", "Self Improvement Daily", "spotify", "https://open.spotify.com/episode/reading1", None, 25, None, None, ["reading","habits","self-help"], True),
        ]
        books_db = db.query(Book).all()
        for title, host, platform, url, embed, duration, season, episode, tags, featured in podcast_data:
            book_id = None
            for b in books_db:
                if b.title.lower().startswith(title.split(":")[0].strip().lower()[:15]):
                    book_id = b.id
                    break
            db.add(PodcastEpisode(book_id=book_id, title=title, host=host, platform=platform, audio_url=url, embed_url=embed, duration_minutes=duration, season_number=season, episode_number=episode, tags=tags, is_featured=featured, published_date=date.today(), thumbnail_url=f"https://placehold.co/480x360/4f46e5/ffffff?text={title.replace(' ','+')[:30]}"))

        playlist_data = [
            ("BookTube Essentials", "Curated book reviews and deep dives", "youtube", "BookTube Channel", "https://youtube.com/@booktube", True, 0, [
                ("Atomic Habits Book Review", "https://youtu.be/PZ7lDrwYdZc", "https://www.youtube.com/embed/PZ7lDrwYdZc", 15, "youtube"),
                ("Sapiens in 10 Minutes", "https://youtu.be/CjVQJirIrG0", "https://www.youtube.com/embed/CjVQJirIrG0", 10, "youtube"),
                ("Deep Work Summary", "https://youtu.be/deep1", "https://www.youtube.com/embed/deep1", 12, "youtube"),
                ("Think and Grow Rich Guide", "https://youtu.be/think1", "https://www.youtube.com/embed/think1", 20, "youtube"),
                ("The Alchemist Explained", "https://youtu.be/alchemist1", "https://www.youtube.com/embed/alchemist1", 8, "youtube"),
            ]),
            ("BookTok Viral Hits", "Trending book videos from TikTok", "tiktok", "BookTok", "https://tiktok.com/@booktok", True, 1, [
                ("Atomic Habits in 60s", "https://tiktok.com/@booktok/video/1", None, 1, "tiktok"),
                ("Books That Changed My Life", "https://tiktok.com/@booktok/video/2", None, 2, "tiktok"),
                ("Rich Dad Poor Dad Review", "https://tiktok.com/@booktok/video/3", None, 1, "tiktok"),
                ("5 Books Everyone Should Read", "https://tiktok.com/@booktok/video/4", None, 3, "tiktok"),
            ]),
            ("Bookstagram Reels", "Instagram book reels and reviews", "instagram", "Bookstagram", "https://instagram.com/bookstagram", True, 2, [
                ("Daily Reading Routine", "https://instagram.com/reel/book1", None, 1, "instagram"),
                ("Book Haul 2024", "https://instagram.com/reel/book2", None, 2, "instagram"),
                ("Best Self-Help Books", "https://instagram.com/reel/book4", None, 2, "instagram"),
            ]),
            ("Author Interviews", "Conversations with top authors", "youtube", "Author Spotlight", "https://youtube.com/@authorspotlight", False, 3, [
                ("Interview: James Clear on Habits", "https://youtu.be/int1", "https://www.youtube.com/embed/int1", 30, "youtube"),
                ("Cal Newport on Deep Work", "https://youtu.be/int2", "https://www.youtube.com/embed/int2", 25, "youtube"),
                ("Morgan Housel on Money", "https://youtu.be/int3", "https://www.youtube.com/embed/int3", 28, "youtube"),
            ]),
            ("Tech Unboxed", "Electronics and gadget reviews", "youtube", "Tech Reviews", "https://youtube.com/@techreviews", True, 4, [
                ("iPhone 15 Pro Max Review", "https://youtu.be/tech1", "https://www.youtube.com/embed/tech1", 20, "youtube"),
                ("MacBook Pro M3 Deep Dive", "https://youtu.be/tech2", "https://www.youtube.com/embed/tech2", 25, "youtube"),
                ("Best Noise Cancelling Headphones", "https://youtu.be/tech3", "https://www.youtube.com/embed/tech3", 18, "youtube"),
            ]),
        ]

        for pname, pdesc, plat, channel, channel_url, featured, order, videos in playlist_data:
            playlist = VideoPlaylist(name=pname, description=pdesc, platform=plat, channel_name=channel, channel_url=channel_url, is_featured=featured, sort_order=order, thumbnail_url=f"https://placehold.co/800x400/7c3aed/ffffff?text={pname.replace(' ','+')}")
            db.add(playlist)
            db.flush()
            for i, (vtitle, vurl, vembed, vdur, vplat) in enumerate(videos):
                db.add(PlaylistVideo(playlist_id=playlist.id, title=vtitle, url=vurl, embed_url=vembed, duration_minutes=vdur, platform=vplat, sort_order=i, view_count=0, thumbnail_url=f"https://placehold.co/480x360/1e40af/ffffff?text={vtitle.replace(' ','+')[:25]}"))

        today = date.today()
        from datetime import timedelta
        cricfy_matches = [
            CricfyMatch(title="🏆 ICC World Cup 2026: India vs Australia", team1="India", team2="Australia", team1_logo="https://placehold.co/80x80/ff9933/ffffff?text=IND", team2_logo="https://placehold.co/80x80/ffcc00/000000?text=AUS", match_date=today, match_time="14:30 IST", status="live", series_name="ICC World Cup 2026", venue="Wankhede Stadium, Mumbai", live_url="https://www.youtube.com/watch?v=example1", embed_url="https://www.youtube.com/embed/example1", thumbnail_url="https://placehold.co/640x360/1e40af/ffffff?text=IND+vs+AUS", platform="youtube", score_team1="245/4", score_team2="120/2", overs_team1=40.2, overs_team2=22.0, is_featured=True, sort_order=1),
            CricfyMatch(title="🏏 IPL 2026: Mumbai Indians vs Chennai Super Kings", team1="Mumbai Indians", team2="CSK", team1_logo="https://placehold.co/80x80/004d8c/ffffff?text=MI", team2_logo="https://placehold.co/80x80/ffcc00/000000?text=CSK", match_date=today, match_time="19:30 IST", status="live", series_name="IPL 2026", venue="Wankhede Stadium, Mumbai", live_url="https://www.youtube.com/watch?v=example2", embed_url="https://www.youtube.com/embed/example2", thumbnail_url="https://placehold.co/640x360/dc2626/ffffff?text=MI+vs+CSK", platform="youtube", score_team1="180/5", score_team2="45/1", overs_team1=20.0, overs_team2=5.3, is_featured=True, sort_order=2),
            CricfyMatch(title="🏏 ICC World Cup 2026: England vs Pakistan", team1="England", team2="Pakistan", team1_logo="https://placehold.co/80x80/ffffff/000000?text=ENG", team2_logo="https://placehold.co/80x80/00a651/ffffff?text=PAK", match_date=today + timedelta(days=1), match_time="10:00 IST", status="upcoming", series_name="ICC World Cup 2026", venue="Lord's, London", live_url="https://www.youtube.com/watch?v=example3", embed_url="https://www.youtube.com/embed/example3", thumbnail_url="https://placehold.co/640x360/059669/ffffff?text=ENG+vs+PAK", platform="youtube", is_featured=True, sort_order=3),
            CricfyMatch(title="🏏 Asia Cup 2026: Sri Lanka vs Bangladesh", team1="Sri Lanka", team2="Bangladesh", team1_logo="https://placehold.co/80x80/1e40af/ffffff?text=SL", team2_logo="https://placehold.co/80x80/00a651/ffffff?text=BAN", match_date=today + timedelta(days=2), match_time="14:30 IST", status="upcoming", series_name="Asia Cup 2026", venue="R.Premadasa Stadium, Colombo", live_url="https://www.youtube.com/watch?v=example4", embed_url="https://www.youtube.com/embed/example4", thumbnail_url="https://placehold.co/640x360/7c3aed/ffffff?text=SL+vs+BAN", platform="youtube", is_featured=True, sort_order=4),
            CricfyMatch(title="🏏 IPL 2026: Royal Challengers vs Kolkata Knight Riders", team1="RCB", team2="KKR", team1_logo="https://placehold.co/80x80/dc2626/ffffff?text=RCB", team2_logo="https://placehold.co/80x80/3b82f6/ffffff?text=KKR", match_date=today + timedelta(days=1), match_time="19:30 IST", status="upcoming", series_name="IPL 2026", venue="Chinnaswamy Stadium, Bengaluru", live_url="https://www.youtube.com/watch?v=example5", embed_url="https://www.youtube.com/embed/example5", thumbnail_url="https://placehold.co/640x360/d97706/ffffff?text=RCB+vs+KKR", platform="youtube", sort_order=5),
            CricfyMatch(title="🏏 Big Bash League: Sydney Sixers vs Melbourne Stars", team1="Sydney Sixers", team2="Melbourne Stars", team1_logo="https://placehold.co/80x80/ff6600/ffffff?text=SIX", team2_logo="https://placehold.co/80x80/00a3e0/ffffff?text=STA", match_date=today + timedelta(days=3), match_time="08:00 IST", status="upcoming", series_name="Big Bash League 2026", venue="SCG, Sydney", live_url="https://www.youtube.com/watch?v=example6", embed_url="https://www.youtube.com/embed/example6", thumbnail_url="https://placehold.co/640x360/0891b2/ffffff?text=BBL", platform="youtube", sort_order=6),
            CricfyMatch(title="🏏 SA20: Sunrisers Eastern Cape vs MI Cape Town", team1="Sunrisers EC", team2="MI Cape Town", team1_logo="https://placehold.co/80x80/ff6600/ffffff?text=SEC", team2_logo="https://placehold.co/80x80/004d8c/ffffff?text=MICT", match_date=today + timedelta(days=4), match_time="21:00 IST", status="upcoming", series_name="SA20 League", venue="St George's Park, Gqeberha", live_url="https://www.youtube.com/watch?v=example7", embed_url="https://www.youtube.com/embed/example7", thumbnail_url="https://placehold.co/640x360/4f46e5/ffffff?text=SA20", platform="hotstar", sort_order=7),
            CricfyMatch(title="✅ ICC World Cup 2026: New Zealand vs South Africa", team1="New Zealand", team2="South Africa", team1_logo="https://placehold.co/80x80/000000/ffffff?text=NZ", team2_logo="https://placehold.co/80x80/ffa500/ffffff?text=SA", match_date=today - timedelta(days=1), match_time="14:30 IST", status="completed", series_name="ICC World Cup 2026", venue="Seddon Park, Hamilton", live_url="https://www.youtube.com/watch?v=example8", embed_url="https://www.youtube.com/embed/example8", thumbnail_url="https://placehold.co/640x360/059669/ffffff?text=NZ+vs+SA", platform="youtube", score_team1="320/8", score_team2="280/10", overs_team1=50.0, overs_team2=47.3, match_result="New Zealand won by 40 runs", sort_order=8),
            CricfyMatch(title="✅ IPL 2026: Rajasthan Royals vs Delhi Capitals", team1="Rajasthan Royals", team2="Delhi Capitals", team1_logo="https://placehold.co/80x80/ff1493/ffffff?text=RR", team2_logo="https://placehold.co/80x80/0000ff/ffffff?text=DC", match_date=today - timedelta(days=2), match_time="19:30 IST", status="completed", series_name="IPL 2026", venue="Sawai Mansingh Stadium, Jaipur", live_url="https://www.youtube.com/watch?v=example9", embed_url="https://www.youtube.com/embed/example9", thumbnail_url="https://placehold.co/640x360/1e40af/ffffff?text=RR+vs+DC", platform="youtube", score_team1="210/4", score_team2="185/8", overs_team1=20.0, overs_team2=20.0, match_result="Rajasthan Royals won by 25 runs", sort_order=9),
            CricfyMatch(title="✅ T20I: West Indies vs Australia", team1="West Indies", team2="Australia", team1_logo="https://placehold.co/80x80/8b0000/ffffff?text=WI", team2_logo="https://placehold.co/80x80/ffcc00/000000?text=AUS", match_date=today - timedelta(days=3), match_time="06:00 IST", status="completed", series_name="T20I Series", venue="Sabina Park, Jamaica", live_url="https://www.youtube.com/watch?v=example10", embed_url="https://www.youtube.com/embed/example10", thumbnail_url="https://placehold.co/640x360/dc2626/ffffff?text=WI+vs+AUS", platform="youtube", score_team1="175/6", score_team2="178/4", overs_team1=20.0, overs_team2=18.3, match_result="Australia won by 6 wickets", sort_order=10),
        ]
        for match in cricfy_matches:
            db.add(match)

        db.commit()
        books_count = sum(1 for b,_ in all_products if b.product_type=="book")
        elec_count = sum(1 for b,_ in all_products if b.product_type=="electronics")
        cloth_count = sum(1 for b,_ in all_products if b.product_type=="clothing")
        print(f"Seeded {len(categories_data)} categories, {books_count} books, {elec_count} electronics, {cloth_count} clothing, {len(media_data)} media, {len(podcast_data)} podcasts, {len(playlist_data)} playlists, {len(cricfy_matches)} cricfy matches")
    except Exception as e:
        db.rollback()
        print(f"Seed error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed()
