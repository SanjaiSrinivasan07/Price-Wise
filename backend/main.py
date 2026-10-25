from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from sqlalchemy.orm import Session
from .database import Base, engine, get_db, SessionLocal
from .models import Product, Store, Price, Wishlist, PriceAlert
from .schemas import AlertCreate
from .services.comparison import effective_price, pricewise_score
from .ml.predict import estimate_trend

app = FastAPI(title="PriceWise API", version="1.0.0")
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")
Base.metadata.create_all(bind=engine)

def seed():
    db = SessionLocal()

    # Fictional sample stores for a repeatable college demo (not real retailer listings).
    store_names = [
        ("DemoMart", "https://example.com"),
        ("TechStore", "https://example.com"),
        ("ElectroHub", "https://example.com"),
        ("SmartBuy", "https://example.com"),
        ("ValueStore", "https://example.com"),
        ("ClickCart", "https://example.com"),
        ("PriceNest", "https://example.com"),
        ("OfferOrbit", "https://example.com"),
        ("CartCompass", "https://example.com"),
        ("DealDock", "https://example.com"),
        ("ValueLane", "https://example.com"),
        ("PennyPilot", "https://example.com"),
    ]
    stores = []
    for name, website in store_names:
        store = db.query(Store).filter_by(name=name).first()
        if not store:
            store = Store(name=name, website=website)
            db.add(store)
            db.flush()
        stores.append(store)

    product_data = [('ASUS Vivobook 15', 'ASUS', 'Laptop', '15-inch everyday laptop'), ('HP 15s', 'HP', 'Laptop', '15-inch everyday laptop'), ('Lenovo IdeaPad Slim 3', 'Lenovo', 'Laptop', 'Slim productivity laptop'), ('Dell Inspiron 15', 'Dell', 'Laptop', '15-inch productivity laptop'), ('Acer Aspire 5', 'Acer', 'Laptop', 'Performance laptop'), ('Apple MacBook Air M3', 'Apple', 'Laptop', 'Lightweight MacBook'), ('Lenovo LOQ Gaming', 'Lenovo', 'Laptop', 'Gaming laptop'), ('HP Victus Gaming', 'HP', 'Laptop', 'Gaming laptop'), ('Acer Nitro V', 'Acer', 'Laptop', 'Gaming laptop'), ('ASUS TUF Gaming F15', 'ASUS', 'Laptop', 'Gaming laptop'), ('Galaxy S25', 'Samsung', 'Mobile', 'Samsung smartphone'), ('iPhone 16', 'Apple', 'Mobile', 'Apple smartphone'), ('OnePlus 13', 'OnePlus', 'Mobile', 'Android flagship smartphone'), ('Google Pixel 9', 'Google', 'Mobile', 'Google smartphone'), ('Nothing Phone 3', 'Nothing', 'Mobile', 'Smartphone'), ('Samsung Galaxy A56', 'Samsung', 'Mobile', 'Mid-range smartphone'), ('OnePlus Nord 5', 'OnePlus', 'Mobile', 'Mid-range smartphone'), ('Redmi Note 14 Pro', 'Xiaomi', 'Mobile', 'Value smartphone'), ('Realme GT 7', 'Realme', 'Mobile', 'Performance smartphone'), ('Motorola Edge 60', 'Motorola', 'Mobile', 'Android smartphone'), ('Sony WH-1000XM5', 'Sony', 'Headphones', 'Wireless noise-cancelling headphones'), ('JBL Tune 770NC', 'JBL', 'Headphones', 'Wireless noise-cancelling headphones'), ('boAt Rockerz 550', 'boAt', 'Headphones', 'Wireless headphones'), ('Apple AirPods 4', 'Apple', 'Headphones', 'Wireless earbuds'), ('Samsung Galaxy Buds3', 'Samsung', 'Headphones', 'Wireless earbuds'), ('OnePlus Buds Pro 3', 'OnePlus', 'Headphones', 'Wireless earbuds'), ('Sony WF-1000XM5', 'Sony', 'Headphones', 'Premium wireless earbuds'), ('JBL Live 660NC', 'JBL', 'Headphones', 'Wireless headphones'), ('Apple Watch Series 10', 'Apple', 'Smartwatch', 'Apple smartwatch'), ('Samsung Galaxy Watch 7', 'Samsung', 'Smartwatch', 'Android smartwatch'), ('Noise ColorFit Pro', 'Noise', 'Smartwatch', 'Fitness smartwatch'), ('OnePlus Watch 2', 'OnePlus', 'Smartwatch', 'Smartwatch'), ('Amazfit Active 2', 'Amazfit', 'Smartwatch', 'Fitness smartwatch'), ('LG UltraGear 27', 'LG', 'Monitor', '27-inch gaming monitor'), ('Acer Nitro VG271U', 'Acer', 'Monitor', '27-inch gaming monitor'), ('Samsung Odyssey G5', 'Samsung', 'Monitor', 'Curved gaming monitor'), ('Dell S2722QC', 'Dell', 'Monitor', '4K monitor'), ('Logitech K380', 'Logitech', 'Keyboard', 'Wireless keyboard'), ('Redragon K617 Fizz', 'Redragon', 'Keyboard', 'Compact mechanical keyboard'), ('Logitech MX Master 3S', 'Logitech', 'Mouse', 'Wireless productivity mouse'), ('Razer DeathAdder V3', 'Razer', 'Mouse', 'Gaming mouse'), ('Canon EOS R50', 'Canon', 'Camera', 'Mirrorless camera'), ('Sony Alpha ZV-E10', 'Sony', 'Camera', 'Mirrorless camera'), ('JBL Flip 6', 'JBL', 'Speaker', 'Portable Bluetooth speaker'), ('Sony SRS-XB100', 'Sony', 'Speaker', 'Portable Bluetooth speaker'), ('Kindle Paperwhite', 'Amazon', 'Tablet & Reader', 'E-reader'), ('iPad 11th Gen', 'Apple', 'Tablet & Reader', 'Tablet'), ('Samsung Galaxy Tab S10', 'Samsung', 'Tablet & Reader', 'Android tablet')]

    # Expanded catalog: 100+ additional demo products across useful everyday categories.
    extra_products = [
        ("Samsung T7 Shield 1TB", "Samsung", "Storage", "Rugged portable SSD"),
        ("SanDisk Extreme Portable SSD 1TB", "SanDisk", "Storage", "Portable solid-state drive"),
        ("WD Black SN850X 2TB", "Western Digital", "Storage", "High-speed NVMe SSD"),
        ("Crucial X9 Pro 1TB", "Crucial", "Storage", "Compact portable SSD"),
        ("Seagate One Touch 2TB", "Seagate", "Storage", "Portable external hard drive"),
        ("Kingston DataTraveler 128GB", "Kingston", "Storage", "USB flash drive"),
        ("Samsung EVO Plus 256GB", "Samsung", "Storage", "MicroSD memory card"),
        ("Lexar Professional 128GB", "Lexar", "Storage", "High-speed memory card"),
        ("TP-Link Archer AX55", "TP-Link", "Networking", "Wi-Fi 6 router"),
        ("ASUS RT-AX86U", "ASUS", "Networking", "Gaming Wi-Fi router"),
        ("Netgear Nighthawk RAX50", "Netgear", "Networking", "Dual-band Wi-Fi router"),
        ("TP-Link Deco X20 2-Pack", "TP-Link", "Networking", "Mesh Wi-Fi system"),
        ("Google Nest Wifi Pro", "Google", "Networking", "Mesh Wi-Fi router"),
        ("D-Link DAP-X1860", "D-Link", "Networking", "Wi-Fi range extender"),
        ("TP-Link TL-SG108", "TP-Link", "Networking", "8-port network switch"),
        ("Ubiquiti UniFi Express", "Ubiquiti", "Networking", "Compact network gateway"),
        ("PlayStation 5 Slim", "Sony", "Gaming", "Console gaming system"),
        ("Xbox Series X", "Microsoft", "Gaming", "Console gaming system"),
        ("Nintendo Switch OLED", "Nintendo", "Gaming", "Hybrid handheld console"),
        ("Steam Deck OLED 512GB", "Valve", "Gaming", "Portable PC gaming device"),
        ("ASUS ROG Ally", "ASUS", "Gaming", "Windows handheld gaming device"),
        ("Logitech G Pro X Superlight 2", "Logitech", "Gaming", "Lightweight gaming mouse"),
        ("Razer BlackWidow V4", "Razer", "Gaming", "Mechanical gaming keyboard"),
        ("HyperX Cloud III", "HyperX", "Gaming", "Gaming headset"),
        ("Elgato Stream Deck MK.2", "Elgato", "Gaming", "Streaming control pad"),
        ("SteelSeries QcK Large", "SteelSeries", "Gaming", "Gaming mouse pad"),
        ("Corsair RM850e", "Corsair", "PC Components", "850W modular power supply"),
        ("NZXT H5 Flow", "NZXT", "PC Components", "Airflow PC case"),
        ("Noctua NH-D15", "Noctua", "PC Components", "CPU air cooler"),
        ("Corsair Vengeance DDR5 32GB", "Corsair", "PC Components", "Desktop memory kit"),
        ("Samsung Odyssey OLED G8", "Samsung", "Monitor", "OLED gaming monitor"),
        ("BenQ MOBIUZ EX2710Q", "BenQ", "Monitor", "QHD gaming monitor"),
        ("Dell UltraSharp U2723QE", "Dell", "Monitor", "Professional 4K monitor"),
        ("ASUS ProArt PA278CV", "ASUS", "Monitor", "Creator monitor"),
        ("ViewSonic VX3276-2K", "ViewSonic", "Monitor", "Large QHD monitor"),
        ("Logitech Brio 4K", "Logitech", "Webcam", "4K video webcam"),
        ("Anker PowerConf C200", "Anker", "Webcam", "Compact streaming webcam"),
        ("Elgato Facecam Neo", "Elgato", "Webcam", "Full HD creator webcam"),
        ("Canon PIXMA G3770", "Canon", "Printer", "Refillable ink-tank printer"),
        ("Epson EcoTank L3250", "Epson", "Printer", "Wireless ink-tank printer"),
        ("HP LaserJet MFP M236sdw", "HP", "Printer", "Wireless laser printer"),
        ("Brother DCP-T820DW", "Brother", "Printer", "Duplex ink-tank printer"),
        ("Xiaomi Smart Air Purifier 4", "Xiaomi", "Smart Home", "Smart air purifier"),
        ("Philips Hue Starter Kit", "Philips", "Smart Home", "Smart lighting starter kit"),
        ("Amazon Echo Dot 5th Gen", "Amazon", "Smart Home", "Smart speaker"),
        ("Google Nest Hub 2nd Gen", "Google", "Smart Home", "Smart display"),
        ("TP-Link Tapo C225", "TP-Link", "Smart Home", "Indoor security camera"),
        ("Aqara Hub M2", "Aqara", "Smart Home", "Smart home hub"),
        ("SwitchBot Hub 2", "SwitchBot", "Smart Home", "Smart home controller"),
        ("Philips Wiz Smart Bulb 3-Pack", "Philips", "Smart Home", "App-controlled smart bulbs"),
        ("Dyson V8 Origin", "Dyson", "Home Appliances", "Cordless vacuum cleaner"),
        ("Philips Airfryer 3000 Series", "Philips", "Home Appliances", "Air fryer"),
        ("Instant Pot Duo 7-in-1", "Instant Pot", "Home Appliances", "Multi-function pressure cooker"),
        ("Havells Stealth Air Cooler", "Havells", "Home Appliances", "Personal air cooler"),
        ("Mi Robot Vacuum-Mop 2i", "Xiaomi", "Home Appliances", "Robot vacuum cleaner"),
        ("Blue Star 1.5 Ton Inverter AC", "Blue Star", "Home Appliances", "Inverter air conditioner"),
        ("LG 260L Double Door Refrigerator", "LG", "Home Appliances", "Double-door refrigerator"),
        ("IFB 7kg Front Load Washer", "IFB", "Home Appliances", "Front-load washing machine"),
        ("Prestige Iris Mixer Grinder", "Prestige", "Home Appliances", "Mixer grinder"),
        ("Bajaj Majesty OTG 28L", "Bajaj", "Home Appliances", "Countertop oven"),
        ("Garmin Forerunner 165", "Garmin", "Fitness", "GPS running watch"),
        ("Fitbit Charge 6", "Fitbit", "Fitness", "Fitness tracker"),
        ("Decathlon Domyos EB 520", "Domyos", "Fitness", "Indoor exercise bike"),
        ("Boldfit Adjustable Dumbbells", "Boldfit", "Fitness", "Adjustable strength-training set"),
        ("Therabody Theragun Mini", "Therabody", "Fitness", "Portable massage device"),
        ("Withings Body Smart Scale", "Withings", "Fitness", "Connected body scale"),
        ("Anker 737 Power Bank", "Anker", "Accessories", "High-capacity power bank"),
        ("UGREEN Nexode 100W Charger", "UGREEN", "Accessories", "Multi-port USB-C charger"),
        ("Anker 543 USB-C Hub", "Anker", "Accessories", "Multi-port laptop hub"),
        ("Belkin 3-in-1 MagSafe Charger", "Belkin", "Accessories", "Multi-device wireless charger"),
        ("Spigen Tough Armor Case", "Spigen", "Accessories", "Protective phone case"),
        ("Apple USB-C Digital AV Adapter", "Apple", "Accessories", "USB-C display adapter"),
        ("Logitech Pebble Keys 2 K380s", "Logitech", "Keyboard", "Compact multi-device keyboard"),
        ("Keychron K2 Pro", "Keychron", "Keyboard", "Wireless mechanical keyboard"),
        ("Akko 5075B Plus", "Akko", "Keyboard", "Hot-swappable mechanical keyboard"),
        ("Logitech Lift Vertical Mouse", "Logitech", "Mouse", "Ergonomic wireless mouse"),
        ("Microsoft Surface Precision Mouse", "Microsoft", "Mouse", "Precision productivity mouse"),
        ("Razer Orochi V2", "Razer", "Mouse", "Compact wireless gaming mouse"),
        ("Fujifilm Instax Mini 12", "Fujifilm", "Camera", "Instant film camera"),
        ("DJI Osmo Pocket 3", "DJI", "Camera", "Pocket gimbal camera"),
        ("GoPro HERO12 Black", "GoPro", "Camera", "Action camera"),
        ("Nikon Z fc", "Nikon", "Camera", "Mirrorless camera"),
        ("Bose SoundLink Flex", "Bose", "Speaker", "Portable Bluetooth speaker"),
        ("Sonos Era 100", "Sonos", "Speaker", "Wireless home speaker"),
        ("JBL Bar 500", "JBL", "Speaker", "Dolby Atmos soundbar"),
        ("Creative Pebble Pro", "Creative", "Speaker", "Desktop USB speakers"),
        ("Samsung Galaxy Tab A9+", "Samsung", "Tablet & Reader", "Android tablet"),
        ("Lenovo Tab P12", "Lenovo", "Tablet & Reader", "Large-screen Android tablet"),
        ("Xiaomi Pad 6", "Xiaomi", "Tablet & Reader", "Performance Android tablet"),
        ("Boox Note Air3", "Boox", "Tablet & Reader", "E-ink note-taking tablet"),
        ("Apple Pencil USB-C", "Apple", "Accessories", "Tablet stylus"),
        ("Logitech Crayon USB-C", "Logitech", "Accessories", "Digital stylus"),
        ("Jabra Evolve2 65 Flex", "Jabra", "Headphones", "Work-focused wireless headset"),
        ("Sennheiser Momentum 4", "Sennheiser", "Headphones", "Wireless over-ear headphones"),
        ("Soundcore Liberty 4 NC", "Soundcore", "Headphones", "Noise-cancelling earbuds"),
        ("Marshall Emberton III", "Marshall", "Speaker", "Portable wireless speaker"),
        ("Anker Soundcore Motion X600", "Soundcore", "Speaker", "Spatial audio speaker"),
        ("Amazfit Balance", "Amazfit", "Smartwatch", "Health and fitness smartwatch"),
        ("Garmin Venu 3", "Garmin", "Smartwatch", "Fitness smartwatch"),
        ("Samsung Galaxy Fit3", "Samsung", "Fitness", "Slim fitness band"),
        ("OnePlus Pad 2", "OnePlus", "Tablet & Reader", "Large-screen tablet"),
        ("ASUS ZenScreen MB16AC", "ASUS", "Monitor", "Portable USB monitor"),
        ("Epson EF-12 Mini Projector", "Epson", "Projector", "Compact laser projector"),
        ("BenQ TH575 Projector", "BenQ", "Projector", "Full HD home projector"),
        ("XGIMI MoGo 3 Pro", "XGIMI", "Projector", "Portable smart projector"),
        ("Shure MV7+", "Shure", "Audio Equipment", "USB podcast microphone"),
        ("Rode Wireless ME", "Rode", "Audio Equipment", "Wireless microphone system"),
        ("Focusrite Scarlett 2i2 4th Gen", "Focusrite", "Audio Equipment", "USB audio interface"),
        ("Zoom H1essential", "Zoom", "Audio Equipment", "Portable audio recorder"),
    ]
    product_data.extend(extra_products)

    for name, brand, category, description in product_data:
        if not db.query(Product).filter_by(name=name).first():
            db.add(Product(name=name, brand=brand, category=category, description=description))
    db.commit()

    base_prices = {'ASUS Vivobook 15': 45000, 'HP 15s': 46800, 'Lenovo IdeaPad Slim 3': 48600, 'Dell Inspiron 15': 50400, 'Acer Aspire 5': 52200, 'Apple MacBook Air M3': 54000, 'Lenovo LOQ Gaming': 55800, 'HP Victus Gaming': 57600, 'Acer Nitro V': 59400, 'ASUS TUF Gaming F15': 61200, 'Galaxy S25': 39000, 'iPhone 16': 41100, 'OnePlus 13': 43200, 'Google Pixel 9': 45300, 'Nothing Phone 3': 47400, 'Samsung Galaxy A56': 49500, 'OnePlus Nord 5': 51600, 'Redmi Note 14 Pro': 53700, 'Realme GT 7': 55800, 'Motorola Edge 60': 57900, 'Sony WH-1000XM5': 20500, 'JBL Tune 770NC': 21400, 'boAt Rockerz 550': 22300, 'Apple AirPods 4': 23200, 'Samsung Galaxy Buds3': 24100, 'OnePlus Buds Pro 3': 25000, 'Sony WF-1000XM5': 25900, 'JBL Live 660NC': 26800, 'Apple Watch Series 10': 66100, 'Samsung Galaxy Watch 7': 68300, 'Noise ColorFit Pro': 70500, 'OnePlus Watch 2': 72700, 'Amazfit Active 2': 74900, 'LG UltraGear 27': 77700, 'Acer Nitro VG271U': 79600, 'Samsung Odyssey G5': 81500, 'Dell S2722QC': 83400, 'Logitech K380': 20700, 'Redragon K617 Fizz': 21200, 'Logitech MX Master 3S': 30800, 'Razer DeathAdder V3': 31500, 'Canon EOS R50': 198500, 'Sony Alpha ZV-E10': 202000, 'JBL Flip 6': 42200, 'Sony SRS-XB100': 43100, 'Kindle Paperwhite': 108000, 'iPad 11th Gen': 110200, 'Samsung Galaxy Tab S10': 112400}

    category_price_ranges = {
        "Storage": 3500, "Networking": 6500, "Gaming": 18000, "PC Components": 7500,
        "Webcam": 5000, "Printer": 12000, "Smart Home": 4000, "Home Appliances": 18000,
        "Fitness": 6500, "Accessories": 1800, "Projector": 32000, "Audio Equipment": 9000,
        "Monitor": 18000, "Keyboard": 2500, "Mouse": 1800, "Camera": 45000,
        "Speaker": 5000, "Tablet & Reader": 16000, "Headphones": 4500, "Smartwatch": 7000
    }
    for idx, (name, brand, category, description) in enumerate(extra_products):
        base_prices[name] = category_price_ranges.get(category, 8000) + ((idx * 1379) % max(2500, category_price_ranges.get(category, 8000)))

    products = db.query(Product).filter(Product.name.in_([x[0] for x in product_data])).all()
    price_factors = [1.000, 0.970, 1.040, 0.985, 1.020, 0.955, 1.015, 0.990, 1.030, 0.965, 1.008, 0.978]
    discounts =    [10,    15,    8,     12,    5,     7,     11,    9,     6,     14,    4,     13]
    deliveries =   [0,     99,    0,     49,    0,     39,    0,     59,    25,    0,     79,    19]
    ratings =      [4.4,   4.3,   4.5,   4.2,   4.4,   4.1,   4.6,   4.0,   4.3,   4.7,   4.2,   4.5]
    for product in products:
        base = base_prices.get(product.name, 12000)
        existing_store_ids = {row.store_id for row in db.query(Price).filter_by(product_id=product.id).all()}
        # Add any missing store offers even when an older pricewise.db already exists.
        for idx, store in enumerate(stores):
            if store.id in existing_store_ids:
                continue
            price = round(base * price_factors[idx], 2)
            db.add(Price(product_id=product.id, store_id=store.id, price=price,
                         discount=discounts[idx], delivery_charge=deliveries[idx], rating=ratings[idx]))
    db.commit()
    db.close()


@app.get("/api/alerts")
def list_alerts(db: Session = Depends(get_db)):
    rows = db.query(PriceAlert, Product).join(Product, PriceAlert.product_id == Product.id).order_by(PriceAlert.id.desc()).all()
    return [{"id":a.id,"product_id":p.id,"product_name":p.name,"target_price":a.target_price,"active":a.active} for a,p in rows]

@app.delete("/api/alerts/{alert_id}")
def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.get(PriceAlert, alert_id)
    if not alert:
        raise HTTPException(404, "Alert not found")
    db.delete(alert)
    db.commit()
    return {"message":"Price alert deleted"}

seed()

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            "products": products
        }
    )

@app.get("/api/products")
def products(search: str = "", db: Session = Depends(get_db)):
    q = db.query(Product)
    if search:
        q = q.filter(Product.name.ilike(f"%{search}%"))
    return [{"id":p.id,"name":p.name,"brand":p.brand,"category":p.category} for p in q.all()]

@app.get("/api/products/{product_id}")
def product(product_id: int, db: Session = Depends(get_db)):
    p = db.get(Product, product_id)
    if not p: raise HTTPException(404, "Product not found")
    offers = []
    for x in p.prices:
        ep = effective_price(x.price,x.discount,x.delivery_charge)
        offers.append({"store":x.store.name,"price":x.price,"discount":x.discount,"delivery":x.delivery_charge,
                       "rating":x.rating,"effective_price":ep,"score":pricewise_score(ep,x.rating,x.discount),
                       "discount_saving":round(x.price*x.discount/100,2),
                       "deal_dna":round(min(100, pricewise_score(ep,x.rating,x.discount) + (5 if x.delivery_charge == 0 else 0)),1),
                       "recorded_at":x.recorded_at.isoformat()})
    offers=sorted(offers,key=lambda x:x["effective_price"])
    best=offers[0] if offers else None
    return {"product":{"id":p.id,"name":p.name,"brand":p.brand,"category":p.category,"description":p.description},
            "best_offer":best,"offers":offers}

@app.get("/api/decision-lab")
def decision_lab(budget: float = 50000, category: str = "", db: Session = Depends(get_db)):
    """PriceWise signature feature: shortlist products that fit a budget, ranked by value score."""
    results = []
    for p in db.query(Product).all():
        if category and p.category.lower() != category.lower():
            continue
        offers = []
        for offer in p.prices:
            total = effective_price(offer.price, offer.discount, offer.delivery_charge)
            offers.append({"store": offer.store.name, "effective_price": total, "rating": offer.rating, "discount": offer.discount, "delivery": offer.delivery_charge})
        if not offers:
            continue
        best = min(offers, key=lambda x: x["effective_price"])
        if best["effective_price"] <= budget:
            # Deal DNA is a transparent heuristic score, not a guarantee of product quality.
            value = round(min(100, max(0, 55 + best["rating"] * 5 + best["discount"] * 0.8 - (best["delivery"] / max(budget, 1) * 10))), 1)
            results.append({"id":p.id,"name":p.name,"brand":p.brand,"category":p.category,"description":p.description,
                            "best_price":best["effective_price"],"store":best["store"],"rating":best["rating"],
                            "discount":best["discount"],"deal_dna":value,"budget_left":round(budget-best["effective_price"],2)})
    return sorted(results, key=lambda x:(-x["deal_dna"], x["best_price"]))[:30]

@app.get("/api/products/{product_id}/trend")
def trend(product_id: int, db: Session = Depends(get_db)):
    rows = db.query(Price).filter(Price.product_id==product_id).order_by(Price.recorded_at).all()
    return estimate_trend([r.price for r in rows])

@app.post("/api/wishlist/{product_id}")
def add_wishlist(product_id: int, db: Session = Depends(get_db)):
    if not db.get(Product,product_id): raise HTTPException(404,"Product not found")
    if not db.query(Wishlist).filter_by(product_id=product_id).first():
        db.add(Wishlist(product_id=product_id)); db.commit()
    return {"message":"Added to wishlist"}



@app.get("/api/wishlist")
def wishlist(db: Session = Depends(get_db)):
    rows = db.query(Wishlist, Product).join(Product, Wishlist.product_id==Product.id).all()
    return [{"id":p.id,"name":p.name} for _,p in rows]

@app.delete("/api/wishlist/{product_id}")
def remove_wishlist(product_id: int, db: Session = Depends(get_db)):
    item = db.query(Wishlist).filter_by(product_id=product_id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Product not in wishlist")

    db.delete(item)
    db.commit()

    return {"message": "Removed from wishlist"}
@app.post("/api/alerts")
def create_alert(alert: AlertCreate, db: Session = Depends(get_db)):
    if not db.get(Product,alert.product_id): raise HTTPException(404,"Product not found")
    db.add(PriceAlert(product_id=alert.product_id,target_price=alert.target_price))
    db.commit()
    return {"message":"Price alert created","target_price":alert.target_price}
