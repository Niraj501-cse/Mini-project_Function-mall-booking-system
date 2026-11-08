import os
import sys
from app import create_app, db
from app.models import (
    User, CustomerProfile, OwnerProfile, EventCategory, 
    FunctionHall, HallImage, BookingPackage, PackageFeature,
    Booking, Payment, Review, WebsiteSetting, Notification
)
from datetime import datetime, date, timedelta

app = create_app()

def seed_database():
    with app.app_context():
        # Drop all & create all for clean initial seed
        db.drop_all()
        db.create_all()

        print("Seeding users (Admin, Hall Owner, Customers)...")
        # 1. Admin User
        admin = User(
            full_name="Super Admin",
            email="admin@functionmall.com",
            phone="+91 98765 00001",
            role="admin"
        )
        admin.set_password("Admin@123")
        db.session.add(admin)

        # 2. Hall Owner (Configured exactly as requested: owner@checking.com / owner@123)
        owner1 = User(
            full_name="Rajesh Verma (Hall Owner)",
            email="owner@checking.com",
            phone="+91 98765 11111",
            role="owner"
        )
        owner1.set_password("owner@123")
        db.session.add(owner1)

        # 3. Customer User
        customer1 = User(
            full_name="Ananya Sharma",
            email="customer@example.com",
            phone="+91 98765 33333",
            role="customer"
        )
        customer1.set_password("Customer@123")
        db.session.add(customer1)

        db.session.flush()

        # Profiles
        cust_profile = CustomerProfile(
            user_id=customer1.id,
            city="Hyderabad",
            state="Telangana",
            address="Plot 42, Jubilee Hills, Hyderabad",
            preferred_event_type="Wedding"
        )
        db.session.add(cust_profile)

        owner_profile1 = OwnerProfile(
            user_id=owner1.id,
            business_name="Rajesh Royale Function Malls & Conventions",
            business_registration_no="REG-IND-HYD-2018-9901",
            bank_account_no="HDFC00012345678",
            ifsc_code="HDFC0001234",
            is_verified=True
        )
        db.session.add(owner_profile1)
        db.session.flush()

        # 10 Event Categories with EXACTLY 3 realistic, high-res, verified indoor photographs each
        print("Seeding 10 Event Categories with exactly 3 high-res indoor photographs each...")
        categories_data = [
            {
                "slug": "wedding",
                "name": "Wedding / Vivaha Kalyanam",
                "tagline": "Grand Indian Mandaps, Royal Auras & Timeless Vows",
                "description": "Experience breathtaking indoor luxury for your special day. From regal mandap installations to gourmet feast setups, we curate magnificent Indian wedding ceremonies inside climate-controlled banquet halls.",
                "icon": "HeartHandshake",
                "cover": "https://images.unsplash.com/photo-1519741497674-611481863552?auto=format&fit=crop&w=1200&q=80",
                "gallery1": "https://images.unsplash.com/photo-1511285560929-80b456fea0bc?auto=format&fit=crop&w=1200&q=80",
                "gallery2": "https://images.unsplash.com/photo-1519167758481-83f550bb49b3?auto=format&fit=crop&w=1200&q=80"
            },
            {
                "slug": "reception",
                "name": "Grand Reception Gala",
                "tagline": "Glamour, Glitz & Dazzling Post-Wedding Galas",
                "description": "Celebrate love with modern flair. Designer stage backdrops, dynamic intelligent lighting, red-carpet welcomes, and sensational multi-cuisine spreads designed for extraordinary social evenings.",
                "icon": "Sparkles",
                "cover": "https://images.unsplash.com/photo-1464366400600-7168b8af9bc3?auto=format&fit=crop&w=1200&q=80",
                "gallery1": "https://images.unsplash.com/photo-1519225421980-715cb0215aed?auto=format&fit=crop&w=1200&q=80",
                "gallery2": "https://images.unsplash.com/photo-1511795409834-ef04bbd61622?auto=format&fit=crop&w=1200&q=80"
            },
            {
                "slug": "birthday",
                "name": "Birthday & Milestone Celebration",
                "tagline": "Whimsical Themes, Joyful Milestones & Jubilant Memories",
                "description": "Whether celebrating a baby's 1st milestone, sweet sixteen, or a golden jubilee, our vibrant balloon architecture, themed photo booths, and custom dessert tables turn every birthday into magic.",
                "icon": "Cake",
                "cover": "https://images.unsplash.com/photo-1530103862676-de8c9debad1d?auto=format&fit=crop&w=1200&q=80",
                "gallery1": "https://images.unsplash.com/photo-1464349153735-7db50ed83c84?auto=format&fit=crop&w=1200&q=80",
                "gallery2": "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?auto=format&fit=crop&w=1200&q=80"
            },
            {
                "slug": "engagement",
                "name": "Engagement / Nishchitartham",
                "tagline": "Intimate Rings, Romantic Floral Arches & Sacred Beginnings",
                "description": "Mark the official start of your lifelong journey. Elegant floral stage setups, warm ambient candlelight, acoustic entertainment arrangements, and graceful family seating create the most enchanting ring ceremony.",
                "icon": "Gem",
                "cover": "/images/engagement/engagement_grand_stage.jpg",
                "gallery1": "/images/engagement/engagement_floral_arch.jpg",
                "gallery2": "/images/engagement/engagement_banquet_hall.jpg"
            },
            {
                "slug": "baby-shower",
                "name": "Seemantham / Godh Bharai",
                "tagline": "Auspicious Traditions, Bangle Blessings & Maternal Grace",
                "description": "Celebrate the expectant mother with sacred Vedic or modern pastel baby shower traditions. Decorated swing seating, aromatic marigold garlands, traditional brass brassier setups, and wholesome feast planning.",
                "icon": "Baby",
                "cover": "/images/seemantham/seemantham_grand_stage.jpg",
                "gallery1": "/images/seemantham/seemantham_floral_silhouette.png",
                "gallery2": "/images/seemantham/seemantham_baby_bloom.png"
            },
            {
                "slug": "naming-ceremony",
                "name": "Namakaranam / Cradle Ceremony",
                "tagline": "Sacred Cradles, Blessed Names & Cherished Kinship",
                "description": "Namakaran made divine. Luxurious decorated silk cradles, priest arrangements, welcoming floral rangolis, and intimate dining for family members welcoming your newborn star to the world.",
                "icon": "Sun",
                "cover": "/images/naming/naming_grand_stage.jpg",
                "gallery1": "/images/naming/naming_floral_cradle.jpg",
                "gallery2": "/images/naming/naming_swing_cradle.jpg"
            },
            {
                "slug": "anniversary",
                "name": "Anniversary / Shashtipoorthi",
                "tagline": "Golden Milestones, Candlelit Romance & Reaffirmed Love",
                "description": "Toast to 10, 25, 50, or 60 years of companionship. Sophisticated table settings, romantic low-level mood lighting, custom slideshow screens, live violinist/instrumental, and festive family dining.",
                "icon": "Wine",
                "cover": "/images/anniversary/anniversary_grand_stage.jpg",
                "gallery1": "/images/anniversary/anniversary_palace_pavilion.jpg",
                "gallery2": "/images/anniversary/anniversary_floral_aisle.jpg"
            },
            {
                "slug": "corporate-events",
                "name": "Corporate Conclave & Banquet",
                "tagline": "High-Impact Summits, Executive Conclaves & Annual Galas",
                "description": "State-of-the-art corporate venues featuring 4K LED video walls, crystal audio systems, breakout conference suites, high-speed fiber internet, and premium corporate business luncheons.",
                "icon": "Briefcase",
                "cover": "https://images.unsplash.com/photo-1511578314322-379afb476865?auto=format&fit=crop&w=1200&q=80",
                "gallery1": "https://images.unsplash.com/photo-1540575467063-178a50c2df87?auto=format&fit=crop&w=1200&q=80",
                "gallery2": "https://images.unsplash.com/photo-1475721027785-f74eccf877e2?auto=format&fit=crop&w=1200&q=80"
            },
            {
                "slug": "educational-events",
                "name": "Convocation & Educational Gala",
                "tagline": "Grand Convocations, Academic Seminars & Farewell Banquets",
                "description": "Amphitheater and convention hall settings perfect for graduation ceremonies, academic conferences, annual college youth festivals, and award galas with spacious stepped seating and acoustic stages.",
                "icon": "GraduationCap",
                "cover": "https://images.unsplash.com/photo-1523580494863-6f3031224c94?auto=format&fit=crop&w=1200&q=80",
                "gallery1": "https://images.unsplash.com/photo-1524178232363-1fb2b075b655?auto=format&fit=crop&w=1200&q=80",
                "gallery2": "https://images.unsplash.com/photo-1562774053-701939374585?auto=format&fit=crop&w=1200&q=80"
            },
            {
                "slug": "religious-cultural",
                "name": "Satsang, Puja & Cultural Sabha",
                "tagline": "Divine Pujas, Classical Concerts & Spiritual Gatherings",
                "description": "Vibrant traditional spaces crafted for devotional satsangs, classical Carnatic and Hindustani music recitals, temple festivities, and spiritual discourses with sacred decor and pure satvik catering options.",
                "icon": "Flame",
                "cover": "/images/cultural/cultural_grand_stage.jpg",
                "gallery1": "/images/cultural/cultural_dome_hall.jpg",
                "gallery2": "/images/cultural/cultural_classical_sabha.jpg"
            }
        ]

        cat_map = {}
        for idx, cdata in enumerate(categories_data):
            category = EventCategory(
                slug=cdata['slug'],
                name=cdata['name'],
                tagline=cdata['tagline'],
                description=cdata['description'],
                icon_name=cdata['icon'],
                cover_image=cdata['cover'],
                gallery_image_1=cdata['gallery1'],
                gallery_image_2=cdata['gallery2'],
                display_order=idx + 1
            )
            db.session.add(category)
            db.session.flush()
            cat_map[cdata['slug']] = category

        # Seed 10 Packages for EVERY category (Total 100 configured packages)
        print("Seeding 10 distinct packages for each of the 10 categories (100 packages total)...")
        package_specs = {
            "wedding": [
                ("Traditional Vedic Vivaham", "Traditional", 145000, 500, ["Full Vedic Mandap Setup", "Bride & Groom Royal Chairs", "Carnatic Music & Shehnai Setup", "Catering Service Area", "Priest Havankund Zone", "Traditional Entrance Torans"]),
                ("Luxury Rajasthani Vivaha", "Luxury", 285000, 750, ["Exotic Orchids & Lily Mandap", "Red Carpeted Grand Aisle", "LED Video Backdrop", "Bridal Luxury Suite", "Multi-Cuisine Live Stalls Setup", "Intelligent Stage Lighting"]),
                ("Royal Kohinoor Kalyanam", "Royal", 495000, 1200, ["Palatial Maharaja Mandap", "Chandelier Ceiling Drapes", "Drone Photography Access Area", "VIP Lounge Seating", "Live Welcome Orchestra", "Royal Valet Parking Support"]),
                ("Destination-Style Palace Wedding", "Destination", 360000, 600, ["Gazebo Style Floral Pavilion", "Sunset Aisle Illumination", "Boho Luxe Lounge Cabanas", "Signature Mocktail Bar Counters", "Acoustic Stage Setup"]),
                ("Simple Samskara Wedding", "Budget", 65000, 200, ["Compact Floral Mandap", "Stage Sofa & Backdrop", "Essential PA & Mic System", "Standard Guest Chairs", "Dining Hall Support"]),
                ("Indoor AC Royal Wedding", "Indoor", 180000, 450, ["Full AC Central Hall Mandap", "Truss Lighting & Spotlights", "Fiber Floral Wall Backdrop", "Bridal Dressing Room Access", "Generator Power Backup"]),
                ("Emerald Pavilion Wedding", "Pavilion", 220000, 550, ["Lawn Canopy Mandap", "Fairy Light Tunnel Entrance", "Open Air Stage Platform", "All-Weather Tent Covers", "Eco-friendly Lantern Decor"]),
                ("Grand Swarna Mandapam", "Grand", 420000, 1000, ["Magnificent 40ft Stage Mandap", "Automated Floral Shower Setup", "Dual LED Wall Screens", "VVIP Banquet Seating", "Security & Usher Management"]),
                ("Budget Mangalyam Package", "Budget", 48000, 150, ["Neat Satin & Flower Mandap", "Couple Seating Couch", "Clean Hall Furniture Setup", "Basic Audio System", "Dining Furniture"]),
                ("Signature Diamond Wedding", "Premium", 310000, 800, ["Designer Imported Rose Mandap", "Gold-Gilded Stage Thrones", "Fog & Pyro Entry Machines", "Banquet Table Centerpieces", "Professional Sound Stage"])
            ],
            "reception": [
                ("Traditional Sangam Reception", "Traditional", 95000, 400, ["Traditional Brass Lamp Stage", "Marigold & Jasmine Garland Decor", "Grand Couple Swing/Jhula", "Welcome Desk & Gift Zone", "Audio & Mic Setup"]),
                ("Luxury Jodhpuri Reception", "Luxury", 240000, 700, ["Illuminated Glass Runway Stage", "Crystal Drop Chandeliers", "Sparkular Cold Firework Entry", "Curated Velvet Sofa Suite", "Gourmet Dessert Counter Setup"]),
                ("Royal Durbar Reception", "Royal", 390000, 1100, ["Monolithic Victorian Stage", "30ft Panoramic LED Visual Screen", "Executive Dining Enclosure", "Champagne Tower Setup", "Full Sound & Lighting Truss"]),
                ("Evening Star Reception", "Evening", 175000, 500, ["Starlit Sky Ceiling Canopy", "Golden Glow Mood Illumination", "Cocktail High Tables", "Live Saxophone Corner Setup", "Designer Photo Booth"]),
                ("Grand Utsav Reception", "Grand", 320000, 900, ["Colossal 50ft Designer Stage", "Synchronized Moving Head Lights", "Live Stream Video Relay", "VVIP White Leather Couches", "Grand Floral Entrance Arch"]),
                ("Minimalist Pastel Reception", "Minimal", 70000, 250, ["Contemporary Geometric Backdrop", "Warm Edison Bulb Lighting", "Clean Minimalist Couple Seat", "Sleek Welcome Signboard", "Acoustic Audio Setup"]),
                ("Premium Mogra Reception", "Premium", 210000, 600, ["Cascading Floral Wall Stage", "Mirrored Aisle Ramp", "Custom Monogram Gobo Projector", "Round Banquet Tables with Linens", "Live Band Sound Console"]),
                ("Central AC Banquet Reception", "Indoor", 150000, 450, ["Air-Conditioned Grand Hall Setup", "Drape & Shimmer Wall Backdrop", "Ambient LED Par Cans", "Green Rooms for Bride & Groom", "Guest Reception Desk"]),
                ("Grand Ballroom Gala Reception", "Ballroom", 195000, 550, ["Grand Ballroom Stage Setup", "Pergola Stage with Fairy Lights", "Outdoor Buffet Station Setup", "Bistro Lighting Across Lawns", "Barbeque Corner Provision"]),
                ("Budget Milan Reception", "Budget", 45000, 180, ["Satin Drape Stage Backdrop", "Couple 2-Seater Sofa", "Entryway Welcome Standee", "Standard Mic & Speakers", "Clean Banquet Seating"])
            ],
            "birthday": [
                ("Kids Bal Gokul Birthday", "Kids", 35000, 100, ["Cartoon Theme Balloon Arch", "Custom Cutout Characters", "Magic Show & Games Host Arena", "Kids Mini Tables & Chairs", "Popcorn & Candy Floss Zone"]),
                ("First Birthday Shubh Aarambh", "Milestone", 55000, 150, ["Pastel Balloon Wall Backdrop", "Light-Up 'ONE' Letters", "Custom Photo Milestone Board", "Soft Play Zone Area", "Smash Cake Podium Setup"]),
                ("Teen Neon Dhoom Party", "Teen", 48000, 120, ["Neon Glow-in-the-Dark Decor", "Club DJ Console & Moving Lights", "Selfie 360 Spin Booth Setup", "Mocktail Bar Counter", "Lounge Bean Bags"]),
                ("Golden Jubilee 50th Birthday", "Adult", 75000, 200, ["Sophisticated Black & Gold Theme", "Sequin Backdrop with Neon Sign", "Cocktail High Tables", "Acoustic Live Music Setup", "Gourmet Cake Display Stand"]),
                ("Luxury Sheesh Mahal Birthday", "Luxury", 125000, 350, ["Customized Theme Stage Fabrication", "LED Dance Floor Setup", "Celebrity DJ Sound Package", "Professional Event Host", "Themed Photo Souvenir Booth"]),
                ("Cartoon Jungle Safari Party", "Cartoon", 42000, 120, ["Disney/Superhero 3D Cutouts", "Helium Balloon Ceiling Bouquets", "Interactive Tattoos & Face Painting Corner", "Theme Cupcake Stand", "Kids Music Mix"]),
                ("Princess Pari Fairytale Birthday", "Princess", 52000, 140, ["Castle Stage Backdrop", "Pink & White Floral Carriage", "Tiara & Crown Ceremony Props", "Glitter Aisle Carpet", "Fairytale Fairy Lights"]),
                ("Arcade & VR Birthday Arena", "Gaming", 60000, 130, ["PlayStation & VR Corner Booths", "Pixel Art Neon Glow Signage", "Multiplayer Tournament Setup", "Sleek Black Truss Lights", "Burger & Pizza Counters"]),
                ("Surprise Midnight Utsav", "Surprise", 40000, 80, ["Concealed Entrance Curtains", "Synchronized Confetti Blasters", "Hidden Candle Wall Lighting", "Personalized Video Screening", "Midnight Acoustic Singer"]),
                ("Premium Carnival Mela Party", "Premium", 98000, 250, ["Circus Tent Style Canopy", "Carnival Games Stalls (Ring Toss, Darts)", "Juggler & Stilt Walker Arena", "Grand Stage Backdrop", "Dessert Island Buffet"])
            ],
            "engagement": [
                ("Vedic Sagai Traditional", "Traditional", 78000, 250, ["Auspicious Floral Stage Arch", "Silver Urli Candle Water Decor", "Traditional Paan & Supari Trays", "Silk Drapes & Couple Couch", "Mic & Shehnai Audio"]),
                ("Luxury Gulmohar Ring Ceremony", "Luxury", 185000, 500, ["Imported Hydrangea & Rose Ring Arch", "Glass Mirror Ramp Aisle", "Cold Pyrotechnic Ring Exchange Cue", "Dual LED Side Screens", "Designer Ring Platter Display"]),
                ("Royal Nishchitartham Darbar", "Royal", 260000, 750, ["Regal Golden Mandap Ring Stage", "Velvet & Crystal Chandelier Ceiling", "Live Ghazal / Sitar Ensemble", "VIP Velvet Sofa Clusters", "Drone Coverage Lighting"]),
                ("Indoor Floral Engagement", "Indoor", 135000, 350, ["Rustic Wooden Floral Arbour", "Vintage Fairy Light Trees", "Chiavari Chairs with Satin Bows", "Ring Ceremony Stage", "Acoustic Duo Corner"]),
                ("Minimalist Chandan Engagement", "Minimal", 65000, 180, ["Blush Pink & Peach Wave Backdrop", "Sleek Gold Ring Frame Decor", "Modern Geometric Pedestals", "Ambient Warm Wash Lighting", "Custom Calligraphy Signage"]),
                ("Grand Panorama Engagement", "Terrace", 110000, 250, ["Pergola Floral Setup", "Golden Hour Photography Lights", "Cocktail Seating with High Stools", "Custom Monogram Projection", "Surround Sound Ambient System"]),
                ("Floral Fantasy Engagement", "Floral", 165000, 400, ["10,000 Fresh Stem Flower Wall", "Floral Chandelier Chuppah", "Aisle Carpeted with Rose Petals", "Elegant Couple Loveseat", "Subtle Fragrance Dispensers"]),
                ("Grand Mandapam Ring Ceremony", "Ballroom", 225000, 600, ["Centrally Air-Conditioned Stage Extravaganza", "Truss Lighting with Spot Profiles", "Digital Stage Backdrop", "VVIP Banquet Table Layout", "Welcome Receptionist Desk"]),
                ("Budget Subhakaryam Engagement", "Budget", 38000, 100, ["Clean Satin & Marigold Ring Stage", "Comfortable Couple 2-Seater", "Essential PA Sound System", "50 Banquet Chairs & Covers", "Dining Area Furniture"]),
                ("Signature Kohinoor Engagement", "Signature", 195000, 450, ["Diamond Shaped LED Light Arc", "Mirror Floor Stage", "Dry Ice Low Smoke Machine", "Custom Acrylic Ring Pedestal", "Live String Quartet Setup"])
            ],
            "baby-shower": [
                ("Vedic Seemantham Traditional", "Traditional", 68000, 200, ["Sacred Floral Swing (Jhula)", "Traditional Brass Kuthuvilakku Lamps", "Kolam / Rangoli Entrance Art", "Marigold & Mango Leaf Torans", "Priest Puja Platform Setup"]),
                ("Royal Mother-to-Be Godh Bharai", "Royal", 155000, 450, ["Regal Floral Canopy with Swing", "Gold Zari Drapes Backdrop", "Personalized Blessing Stage", "Orchestra/Bhajan Audio Setup", "VIP Sofa Seating for Elders"]),
                ("Pastel Balloon & Floral Shower", "Modern", 72000, 200, ["Gender-Neutral Pastel Balloon Arches", "Floral 'Baby' Marquee Letters", "Cute Teddy Bear Prop Accents", "Mother's Crown & Sash Props", "Dessert Table Styling"]),
                ("Saubhagya Godh Bharai Gala", "Traditional", 85000, 250, ["Rich Saffron & Green Floral Theme", "Embroidered Silk Cushion Seating", "Traditional Bangle Ceremony Counter", "Shehnai & Dholak Audio Station", "Grand Welcome Toran"]),
                ("Garden Boho Baby Shower", "Boho", 92000, 220, ["Rattan Cane Chairs & Pampas Grass", "Dreamcatcher Stage Backdrop", "Picnic Style Low Seating Tables", "Fairy Light Canopies", "Fresh Fruit & Juice Bar Setup"]),
                ("Grand Kutumbam Seemantham", "Grand", 130000, 380, ["Multi-Tier Floral Stage Backdrop", "Air Conditioned Banquet Layout", "Live Stream Cameras for Relatives", "Stage Ramp for Elder Blessings", "Complete Catering Hall Setup"]),
                ("Budget Auspicious Shower", "Budget", 34000, 100, ["Simple Flower Jhula / Swing", "Traditional Silk Cloth Backdrop", "Audio Speaker for Mantras", "Standard Seating for 80 Guests", "Dining Area Provision"]),
                ("Sweet Lavender Baby Shower", "Themed", 62000, 180, ["Lavender & White Drapes", "Cascading Wisteria Flower Vines", "Photo Booth with Mom-to-Be Props", "Soft Acoustic Music Playlist", "Custom Cake Stand Table"]),
                ("Luxury Blessing Ceremony", "Luxury", 175000, 500, ["Designer Fresh Flower Swing Art", "Chandelier-lit Central Pavilion", "Live Classical Flute Performance", "Gourmet Satvik Feast Counters", "VIP Lounge Enclaves"]),
                ("Haritha Organic Eco Shower", "Eco", 58000, 150, ["Banana Trunk & Coconut Leaf Art", "Earthen Pot Floral Centerpieces", "Khadi Silk Drapes", "Organic Herbal Tea Counter", "Biodegradable Decor Props"])
            ],
            "naming-ceremony": [
                ("Divya Namakaran Ceremony", "Traditional", 52000, 180, ["Decorated Wooden/Brass Cradle", "Sacred Homa Kund Safety Setup", "Floral Rangoli Circle for Baby", "Priest & Family Ceremony Stage", "Mantra Audio System"]),
                ("Royal Silk Cradle Utsav", "Royal", 120000, 400, ["Velvet & Gold Embroidered Cradle", "Exotic Lotus & Jasmine Stage Arch", "Live Shehnai & Nadaswaram Group", "Grand Dining Banquet Decor", "VIP Family Lounges"]),
                ("Starlit Cradle Wonderland", "Modern", 68000, 220, ["Suspended Floral Ring with Fairy Lights", "Cloud & Crescent Moon Backdrop", "Illuminated Baby Name Reveal Board", "Soft Cozy Rug Flooring", "Custom Keepsake Desk"]),
                ("Auspicious Cradle & Puja", "Traditional", 60000, 200, ["Traditional Mango Leaf & Marigold Setup", "Brass Oil Lamps (Diya) Station", "Astrologer / Pandit Desk Support", "Family Seating Mats & Chairs", "Chanting Audio PA"]),
                ("Ananda Cradle Celebration", "Garden", 75000, 250, ["Floral Cradle Hanging Setup", "Pastel Sunshade Canopies", "Charming Welcome Chalkboard Sign", "High Tea & Snack Station", "Gentle Acoustic Background Music"]),
                ("Grand Heritage Namakaran", "Heritage", 140000, 450, ["Carved Temple Pillar Replica Backdrop", "Silver Cradle with Silk Canopy", "Live Classical Carnatic Trio", "Elaborate Buffet Dining Area", "Photographer Portrait Enclosure"]),
                ("Budget Naming Ceremony", "Budget", 30000, 90, ["Neat Decorated Baby Cradle", "Simple Satin Draped Stage", "Standard PA System for Blessings", "Comfortable Seating for 70", "Clean Dining Space"]),
                ("Floral Chariot Cradle", "Themed", 88000, 280, ["Miniature Floral Rath/Chariot for Baby", "Rose Petal Carpeted Stage", "Baby Crown & Blessing Props", "Surround Sound Music System", "Customized Cake Table"]),
                ("Luxury Sovereign Naming", "Luxury", 160000, 500, ["Designer Gold Cradle Creation", "Floral Waterfall Backdrop", "LED Screen for Live Cradle View", "Gourmet Welcome Refreshments", "Dedicated Mother-Baby Room"]),
                ("Intimate Home-Style Ceremony", "Intimate", 38000, 120, ["Cosy Cushioned Stage Platform", "Warm Amber Spotlight Decor", "Fresh Lily Flower Garland Accents", "Compact Sound System", "Baby Keepsake Guestbook Area"])
            ],
            "anniversary": [
                ("Silver Jubilee 25th Gala", "Jubilee", 135000, 350, ["Silver Shimmer Wall & 25 Neon Sign", "White Rose & Eucalyptus Arches", "Couple Memory Timeline Gallery", "Live Instrumental Band Console", "Champagne Toast Tables"]),
                ("Shashtipoorthi 60th Shanti", "Traditional", 220000, 600, ["Grand Gold Gilded Stage Pillars", "Priest Kalash Puja Dais", "Family Video Tribute Big Screen", "Royal Couple Throne Chairs", "Satvik Feast Dining"]),
                ("Romantic Candlelight Soiree", "Romantic", 85000, 180, ["100+ Safe LED Candlelit Pathway", "Cascading Fairy Light Backdrop", "Heart-Shaped Floral Centerpiece", "Acoustic Solo Guitarist Setup", "Intimate Couple Dining Table"]),
                ("Luxury Ballroom Anniversary", "Luxury", 195000, 500, ["AC Ballroom Ceiling Drapery", "Intelligent Mood Color Lights", "Sparkling Entry Pyrotechnics", "Cocktail High Tables & Velvet Bar", "Full Sound & DJ Setup"]),
                ("Garden Glow Anniversary", "Garden", 110000, 300, ["Bistro Lit Open-Air Lawn", "Wooden Gazebo Stage with Vines", "Lantern Centerpieces on Linen Tables", "Live BBQ Provision Corner", "Rustic Photobooth Frame"]),
                ("Vintage Nostalgia Celebration", "Vintage", 95000, 220, ["Retro Vinyl & Gramophone Accents", "Sepia-Toned Photo Memory Wall", "Classic Chesterfield Leather Sofa", "Oldies Melody Sound Curation", "Wine & Dessert Display"]),
                ("Grand Ruby 40th Gala", "Grand", 160000, 420, ["Deep Crimson & Gold Stage Decor", "Red Carpet Entrance with Velvet Ropes", "Double Projector Slide Screens", "Comfortable Elder Lounges", "Grand Buffet Area Layout"]),
                ("Budget Intimate Anniversary", "Budget", 36000, 90, ["Draped Fabric Stage Backdrop", "Floral Ring Frame with Couple Names", "PA Speaker with Mic for Speeches", "Standard Table & Chair Setup", "Cake Table Setup"]),
                ("Terrace Starlight Romance", "Terrace", 125000, 250, ["Under-the-Stars Rooftop Pavilion", "Fiber Optic Star Ceiling Canopies", "Personalized Love Story Gobo Light", "Lounge Low-Seating Couches", "Soft Jazz Sound Setup"]),
                ("Signature Diamond Anniversary", "Signature", 250000, 650, ["Diamond Faceted Stage Columns", "Spectacular Central Light Canopy", "Live Violin & Cello Performance", "Five-Star Banquet Dining Layout", "VIP Welcome Escort"])
            ],
            "corporate-events": [
                ("Annual Business Summit", "Summit", 165000, 400, ["Large Seamless LED Video Wall (16x9)", "Dual Presentation Podiums with Mics", "Comfortable Theater-Style Seating", "Live Webcast & Recording Support", "High-Speed Wi-Fi Zone Provision"]),
                ("Executive Leadership Conclave", "Executive", 125000, 200, ["Round Banquet Tables with Notepads", "Acoustic Noise-Isolated Hall", "Digital Presentation Pointer Systems", "Executive Buffet Dining Enclosure", "VIP Speaker Holding Room"]),
                ("Corporate Product Launch", "Launch", 240000, 600, ["Dramatic Reveal Curtain & Lighting", "Dynamic RGB Stage Spotlights", "Product Display Pedestals with Risers", "Media Press Backdrop (Step & Repeat)", "High-Fidelity Surround Sound"]),
                ("Annual Corporate Gala & Awards", "Awards", 210000, 550, ["Red Carpet Gala Arrival Runway", "Golden Trophy Display Showcase", "Concert Level Truss Lighting & DJ", "LED Trophy Award Screen Graphics", "Banquet Dining Setup with Linen"]),
                ("Professional Training Seminar", "Seminar", 65000, 150, ["Dual HD Projectors & Screens", "Collar & Cordless Microphones (4x)", "Classroom Style Tables with Power", "Tea/Coffee Break Station", "Registration & Badge Counter"]),
                ("Corporate Townhall Meet", "Townhall", 95000, 300, ["Central Stage with 360-degree Mic", "Dual Delay Audio Speakers", "Company Branding Banners", "Audience Q&A Wireless Mics (4x)", "Refreshment Service Layout"]),
                ("Startup Pitch Fest", "Pitch", 85000, 250, ["Sleek Minimalist Stage & Bar Stools", "Timer & Presentation Display", "Investor Lounge Enclosure", "Demo Pods for Exhibitors", "Fast Gigabit Network Backbone"]),
                ("Luxury CXO Networking Dinner", "Dinner", 150000, 180, ["Candlelit Premium Round Tables", "Fine China Place Setting Logistics", "Soft Instrumental Background Sound", "Private Bar & Lounge Counters", "Valet Parking Management"]),
                ("Budget Corporate Meeting", "Budget", 42000, 90, ["Standard Projector & Pull-down Screen", "Speaker Podium with Goose Mic", "Rows of 80 Cushioned Chairs", "Whiteboard & Marker Stands", "Water & Tea Station Area"]),
                ("Global Multi-Hub Conference", "Global", 290000, 800, ["Dual LED Walls with Video Call Hub", "Simultaneous Translation Audio Booths", "Studio Quality Broadcast Cameras", "Exhibition Booth Partitions", "Green Room for Keynote VIPs"])
            ],
            "educational-events": [
                ("Grand College Convocation", "Convocation", 175000, 700, ["Dignitary Stage for 25 Deans/VIPs", "Large LED Screen for Scroll Reading", "Staged Stepped Aisle for Graduates", "Procession March PA Sound System", "Photo Studio Booth for Degree Portraits"]),
                ("Annual College Cultural Fest", "Cultural", 230000, 1000, ["Rock Band Stage Rigging & Truss", "Heavy Duty Subwoofers & Line Array", "Intelligent Sharpy Moving Light Beams", "Green Rooms for Performing Troupes", "Crowd Control Barricade System"]),
                ("Academic Farewell Gala", "Farewell", 90000, 350, ["Nostalgia Memory Video Wall", "DJ Dance Floor & Sound System", "Selfie Zone with Fun Props", "Student King/Queen Stage Titles", "Fast Food & Buffet Station Setup"]),
                ("National Academic Conference", "Conference", 120000, 450, ["Keynote Podium & Laser Screens", "Poster Presentation Exhibit Boards", "Faculty Dining Banquet Area", "Microphones for Hall Interventions", "Registration & Kit Distribution Area"]),
                ("School Annual Day Spectacular", "AnnualDay", 145000, 800, ["Wide 60ft Stage for 50 Child Performers", "Side Wings & Changing Dressing Rooms", "Bright Clean Stage Floodlighting", "Parent Seating Layout for 800", "High Clarity Narration Sound"]),
                ("Youth Leadership Symposium", "Symposium", 78000, 280, ["Panelist Semi-Circular Stage Chairs", "Catch-box Throwing Mics for Youth", "Digital Presentation Screen", "Discussion Roundtable Layout", "Healthy Snack & Beverage Station"]),
                ("Alumni Homecoming Reunion", "Reunion", 110000, 400, ["Decade Flashback Wall Installations", "Cocktail & Dinner Seating Mix", "Acoustic Band Stage Setup", "Alumni Association Registration Desk", "Memento Souvenir Station"]),
                ("Inter-College Debate & Elocution", "Debate", 55000, 200, ["Dual Affirmative / Opposing Podiums", "Time Bell & Countdown Digital Display", "Judges Table with Spot Lighting", "Audience Gallery Seating", "Crystal Clear Voice Acoustics"]),
                ("Budget Seminar Hall Setup", "Budget", 38000, 150, ["Standard AV System with Screen", "Single Speaker Podium", "150 Stackable Chairs", "Clean Dais Stage with Green Cloth", "Water Bottles & Glasses Support"]),
                ("Varsity Sports & Arts Gala", "Gala", 160000, 600, ["High Impact Stage with Trophy Risers", "Energetic Light & Sound Show", "Grand Entryway for Athletes", "Food Court Canopy Provision", "Large Group Photo Area"])
            ],
            "religious-cultural": [
                ("Traditional Temple Puja & Homa", "Traditional", 72000, 300, ["Certified Fire-Safe Homa Kund Zone", "Fresh Banana Trunks & Marigold Pillars", "Sacred Mandap with Brass Idols Setup", "Devotional Bhajan Audio System", "Prasadam Distribution Counter"]),
                ("Grand Devotional Satsang", "Satsang", 130000, 600, ["Elevated Guru Dais with White Silk", "Padded Floor Seating Carpets", "Surround Sound Echo-Free PA", "Devotee Shoe Counter & Cloakroom", "Pure Satvik Bhojan Hall Setup"]),
                ("Classical Carnatic / Dance Arangetram", "Arangetram", 115000, 450, ["Acoustically Treated Wooden Stage", "Nataraja Idol & Brass Deepams", "Musicians Dais with Specialized Mics", "Warm Amber Footlights & Spotlights", "Green Room for Costume Changes"]),
                ("Festive Navratri Dandiya Raas", "Festival", 195000, 900, ["Expansive Wooden/Smooth Dance Arena", "Vibrant Gujarati Toran & Mirror Decor", "High-Energy Folk Orchestra Sound Console", "Intelligent Color Wash Beams", "Traditional Snack & Chaat Stalls"]),
                ("Divine Bhagavata Saptaham", "Discourse", 140000, 500, ["Grand Vyasa Peetham Dais Setup", "7-Day Continuous Audio PA Tuning", "Spacious Floor Mats + Elderly Chairs", "Large LED Relay Screens for Discourse", "Daily Anna Prasadam Dining Lines"]),
                ("Diwali & Deepavali Grand Mela", "Festival", 165000, 700, ["1000+ Earthen Diyas Illumination", "Vibrant Rangoli Competition Arena", "Sparkler & Safe Fireworks Zone", "Traditional Sweet & Savory Stalls", "Festive Folk Dance Stage"]),
                ("Jagannath Rath & Kirtan Utsav", "Utsav", 125000, 550, ["Altar Canopy with Silk Draperies", "Kirtan Accordion / Mridanga Sound Mix", "Procession Pathway Arrangement", "Large Chappan Bhog Offering Table", "Prasad Serving Area"]),
                ("Sufi & Qawwali Mystical Night", "Cultural", 155000, 480, ["Low Diwan Carpeted Seating with Bolsters", "Soft Red & Amber Moroccan Lamps", "Qawwal Stage with Harmonium Mics", "Mughlai Dining Banquet Setup", "Incense & Ittar Scented Ambience"]),
                ("Budget Community Puja", "Budget", 39000, 150, ["Clean Puja Altar with Flower Decor", "Standard PA Box Speakers for Mantras", "Carpeted Floor Area for 100 Devotees", "Prasadam Table with Covers", "Clean Wash Area"]),
                ("Grand Maha Kumbhabhishekam Sabha", "MahaSabha", 260000, 1200, ["Massive Covered Pandal Stage", "Vedic Scholar Dais for 50 Priests", "High Capacity Megaphone & Line Arrays", "VVIP Seating + Mass Congregation Area", "Mass Dining Layout for 1000+"])
            ]
        }

        # Populate the 100 packages
        for slug, pkgs in package_specs.items():
            cat = cat_map[slug]
            for (pname, tier, price, capacity, feats) in pkgs:
                pkg = BookingPackage(
                    category_id=cat.id,
                    name=pname,
                    tier=tier,
                    description=f"Comprehensive {pname} crafted specially for {cat.name}. Includes indoor banquet hall setup, tailored stage decoration, audio-visual support, and experienced hospitality staff.",
                    base_price=float(price),
                    guest_capacity=capacity,
                    price_per_plate_veg=450.0 + (50.0 if "Luxury" in tier or "Royal" in tier else 0.0),
                    price_per_plate_nonveg=650.0 + (100.0 if "Luxury" in tier or "Royal" in tier else 0.0),
                    food_menu_summary="Welcome drinks, 3 starters, 2 main curries, dal makhani, fragrant pulao, assortment of breads, 2 dessert specials.",
                    decoration_details="Fresh seasonal florals, thematic stage backdrop, ambient lighting, entrance arch, and coordinated table linens.",
                    image_url=cat.cover_image,
                    is_popular=("Royal" in tier or "Luxury" in tier or "Traditional" in tier)
                )
                db.session.add(pkg)
                db.session.flush()

                for f in feats:
                    feat = PackageFeature(package_id=pkg.id, feature_text=f)
                    db.session.add(feat)

        # 6. Realistic Indian Function Halls & Convention Malls (Indoor Banquet Setups)
        print("Seeding authentic Indian Function Malls & Convention Palaces...")
        halls_data = [
            {
                "name": "Sri Raja Rajeshwari Kalyana Mandapam & Function Mall",
                "slug": "sri-raja-rajeshwari-kalyana-mandapam-hyderabad",
                "owner_id": owner_profile1.id,
                "city": "Hyderabad",
                "area": "Kukatpally Housing Board (KPHB)",
                "address": "Phase 3, Near Temple Bus Stop, KPHB Colony, Hyderabad, Telangana 500072",
                "tagline": "Grand South Indian Mandaps, Royal Auras & AC Banquet Dining",
                "desc": "Sri Raja Rajeshwari Kalyana Mandapam is Hyderabad's premier indoor celebration mall. Featuring pure teakwood stage pillars, centrally air-conditioned 1,500-guest main convention hall, dedicated homa kund facility, 8 bridal guest suites, and separate multi-tier traditional vegetarian dining hall.",
                "min_cap": 200,
                "max_cap": 1600,
                "rent": 145000.0,
                "advance": 25.0,
                "facilities": "Central Air Conditioning, Valet Parking (350 Cars), 8 AC Bridal Suites, 100% DG Power Backup, Separate Dining Hall, In-house Sound Truss, Dedicated Priest Room, Passenger & Freight Elevators",
                "supported": "wedding,reception,engagement,baby-shower,naming-ceremony,religious-cultural",
                "rating": 4.9,
                "reviews": 142,
                "featured": True,
                "images": [
                    "https://images.unsplash.com/photo-1519167758481-83f550bb49b3?auto=format&fit=crop&w=1200&q=80",
                    "https://images.unsplash.com/photo-1519741497674-611481863552?auto=format&fit=crop&w=1200&q=80",
                    "https://images.unsplash.com/photo-1511795409834-ef04bbd61622?auto=format&fit=crop&w=1200&q=80"
                ]
            },
            {
                "name": "Maharaja Palace Convention & Grand Function Mall",
                "slug": "maharaja-palace-convention-mall-bangalore",
                "owner_id": owner_profile1.id,
                "city": "Bengaluru",
                "area": "Jayanagar 4th Block",
                "address": "12th Main Road, Near South End Circle, Jayanagar, Bengaluru, Karnataka 560011",
                "tagline": "Royal Darbar Architecture for Luxury Receptions & Weddings",
                "desc": "Built with opulent palace arches, Italian marble flooring, Swarovski crystal chandeliers, and expansive column-free viewing. Ideal for grand wedding receptions, ring ceremonies, and milestone celebrations with royal hospitality.",
                "min_cap": 150,
                "max_cap": 1400,
                "rent": 165000.0,
                "advance": 20.0,
                "facilities": "Central Air Conditioning, Ample Parking (250 cars), Wi-Fi 6 Enabled, HD LED Wall Screens, Modern Audio-Visual Console, Changing Suites, Modern Kitchen Facility",
                "supported": "wedding,reception,birthday,engagement,anniversary,corporate-events",
                "rating": 4.8,
                "reviews": 118,
                "featured": True,
                "images": [
                    "https://images.unsplash.com/photo-1464366400600-7168b8af9bc3?auto=format&fit=crop&w=1200&q=80",
                    "https://images.unsplash.com/photo-1519225421980-715cb0215aed?auto=format&fit=crop&w=1200&q=80",
                    "https://images.unsplash.com/photo-1511285560929-80b456fea0bc?auto=format&fit=crop&w=1200&q=80"
                ]
            },
            {
                "name": "Shubham Royal Banquet & Celebration Hall",
                "slug": "shubham-royal-banquet-hall-hyderabad",
                "owner_id": owner_profile1.id,
                "city": "Hyderabad",
                "area": "Banjara Hills, Road No. 10",
                "address": "Near Star Hospitals, Road No. 10, Banjara Hills, Hyderabad, Telangana 500034",
                "tagline": "Elegant Intimate Celebrations, Birthday Galas & Seemantham",
                "desc": "A boutique luxury indoor hall tailored for family milestones: cradle ceremonies, traditional Seemantham, engagements, and vibrant kids birthday parties. Fitted with customized warm fairy lighting and live streaming cameras.",
                "min_cap": 80,
                "max_cap": 600,
                "rent": 75000.0,
                "advance": 25.0,
                "facilities": "Air Conditioned Main Hall, Dedicated Buffet Area, Acoustic Sound System, 2 Green Rooms, Valet Parking, Generator Backup, Modern Stage Lighting",
                "supported": "birthday,baby-shower,naming-ceremony,anniversary,engagement",
                "rating": 4.8,
                "reviews": 89,
                "featured": True,
                "images": [
                    "https://images.unsplash.com/photo-1530103862676-de8c9debad1d?auto=format&fit=crop&w=1200&q=80",
                    "https://images.unsplash.com/photo-1527529482837-4698179dc6ce?auto=format&fit=crop&w=1200&q=80",
                    "https://images.unsplash.com/photo-1520854221256-17451cc331bf?auto=format&fit=crop&w=1200&q=80"
                ]
            },
            {
                "name": "Sri Tirumala Venkateswara Kalyana Vedika",
                "slug": "sri-tirumala-venkateswara-vedika-chennai",
                "owner_id": owner_profile1.id,
                "city": "Chennai",
                "area": "T. Nagar, North Boag Road",
                "address": "No. 88, North Boag Road, T. Nagar, Chennai, Tamil Nadu 600017",
                "tagline": "Traditional Dravidian Sanctity for Auspicious Vivaha Ceremonies",
                "desc": "Designed in pure temple architectural symmetry with hand-carved stone relief panels, sacred havan mandap, nadaswaram dais, and separate pure-vegetarian dining hall adhering to Vedic rituals.",
                "min_cap": 150,
                "max_cap": 1100,
                "rent": 98000.0,
                "advance": 30.0,
                "facilities": "Central AC, Pure Veg Kitchen, Nadaswaram Stage, 6 Guest AC Rooms, Priest Suite, Ample Underground Parking, Lift Access",
                "supported": "wedding,baby-shower,naming-ceremony,religious-cultural,engagement",
                "rating": 4.9,
                "reviews": 134,
                "featured": False,
                "images": [
                    "https://images.unsplash.com/photo-1567157577867-05ccb1388e66?auto=format&fit=crop&w=1200&q=80",
                    "https://images.unsplash.com/photo-1514565131-fce0801e5785?auto=format&fit=crop&w=1200&q=80",
                    "https://images.unsplash.com/photo-1519741497674-611481863552?auto=format&fit=crop&w=1200&q=80"
                ]
            },
            {
                "name": "Veda Vyasa Sabha & Corporate Convention Mall",
                "slug": "veda-vyasa-sabha-convention-mumbai",
                "owner_id": owner_profile1.id,
                "city": "Mumbai",
                "area": "Andheri East, MIDC Central",
                "address": "Plot 45, Cross Road B, MIDC, Andheri East, Mumbai, Maharashtra 400093",
                "tagline": "Executive Business Summits, Convocations & Annual Day Galas",
                "desc": "Top-tier indoor auditorium and banquet center boasting acoustic wall treatment, high-resolution 4K digital backdrops, podium microphone lines, and executive dining facilities suited for corporate and academic gatherings.",
                "min_cap": 100,
                "max_cap": 850,
                "rent": 125000.0,
                "advance": 25.0,
                "facilities": "High-speed Wi-Fi, 4K LED Screen, Professional Sound & Lighting, Valet Parking, Executive Dining Lounge, 2 VIP Lounges, Conference Podiums",
                "supported": "corporate-events,educational-events,anniversary,reception",
                "rating": 4.9,
                "reviews": 92,
                "featured": True,
                "images": [
                    "https://images.unsplash.com/photo-1511578314322-379afb476865?auto=format&fit=crop&w=1200&q=80",
                    "https://images.unsplash.com/photo-1540575467063-178a50c2df87?auto=format&fit=crop&w=1200&q=80",
                    "https://images.unsplash.com/photo-1475721027785-f74eccf877e2?auto=format&fit=crop&w=1200&q=80"
                ]
            }
        ]

        created_halls = []
        for hdata in halls_data:
            hall = FunctionHall(
                owner_id=hdata['owner_id'],
                name=hdata['name'],
                slug=hdata['slug'],
                tagline=hdata['tagline'],
                description=hdata['desc'],
                city=hdata['city'],
                area=hdata['area'],
                full_address=hdata['address'],
                map_location_url="https://maps.google.com/?q=" + hdata['city'],
                min_capacity=hdata['min_cap'],
                max_capacity=hdata['max_cap'],
                base_rent_price=hdata['rent'],
                advance_payment_percentage=hdata['advance'],
                facilities=hdata['facilities'],
                supported_event_types=hdata['supported'],
                rating=hdata['rating'],
                review_count=hdata['reviews'],
                is_featured=hdata['featured'],
                is_approved=True,
                is_active=True
            )
            db.session.add(hall)
            db.session.flush()
            created_halls.append(hall)

            for order, img_url in enumerate(hdata['images']):
                h_img = HallImage(
                    hall_id=hall.id,
                    image_url=img_url,
                    caption=f"{hall.name} - Indoor View {order + 1}",
                    is_primary=(order == 0),
                    display_order=order
                )
                db.session.add(h_img)

        # 7. Seed Sample Bookings
        print("Seeding sample bookings...")
        wedding_pkg = BookingPackage.query.filter_by(name="Royal Kohinoor Kalyanam").first()
        hall1 = created_halls[0]

        b1_date = date.today() + timedelta(days=25)
        b1 = Booking(
            booking_code="FM-2025-0891",
            customer_id=customer1.id,
            hall_id=hall1.id,
            package_id=wedding_pkg.id if wedding_pkg else None,
            event_date=b1_date,
            event_slot="Full Day",
            expected_guests=600,
            event_type="Wedding / Vivaha Kalyanam",
            hall_rent=hall1.base_rent_price,
            package_cost=495000.0,
            catering_cost=270000.0,
            tax_amount=45000.0,
            total_amount=145000.0 + 495000.0 + 270000.0 + 45000.0,
            advance_required=238750.0,
            advance_paid=238750.0,
            balance_amount=716250.0,
            status="Confirmed",
            approval_timestamp=datetime.utcnow() - timedelta(days=2),
            food_choice="Both Veg and Non-Veg",
            notes="Bride and Groom royal entry with traditional nadaswaram musicians."
        )
        db.session.add(b1)
        db.session.flush()

        p1 = Payment(
            transaction_id="pay_FM_test_9921045",
            booking_id=b1.id,
            user_id=customer1.id,
            amount=238750.0,
            payment_type="Advance",
            payment_method="Razorpay Test Mode (UPI / GPay)",
            gateway_order_id="order_FM_test_001",
            gateway_payment_id="pay_FM_test_9921045",
            status="Success",
            is_test_mode=True
        )
        db.session.add(p1)

        # Booking 2: Approved, Awaiting Payment
        b2_date = date.today() + timedelta(days=40)
        reception_pkg = BookingPackage.query.filter_by(name="Luxury Jodhpuri Reception").first()
        b2 = Booking(
            booking_code="FM-2025-1042",
            customer_id=customer1.id,
            hall_id=created_halls[1].id,
            package_id=reception_pkg.id if reception_pkg else None,
            event_date=b2_date,
            event_slot="Evening (5PM - 11PM)",
            expected_guests=400,
            event_type="Grand Reception Gala",
            hall_rent=created_halls[1].base_rent_price,
            package_cost=240000.0,
            catering_cost=180000.0,
            tax_amount=28000.0,
            total_amount=165000.0 + 240000.0 + 180000.0 + 28000.0,
            advance_required=122600.0,
            advance_paid=0.0,
            balance_amount=613000.0,
            status="Awaiting Payment",
            approval_timestamp=datetime.utcnow() - timedelta(hours=3),
            payment_hold_expiry=datetime.utcnow() + timedelta(hours=21),
            food_choice="Both Veg and Non-Veg",
            notes="Please arrange indoor cold-pyro sparklers during cake cutting."
        )
        db.session.add(b2)

        # Booking 3: Pending Approval for Hall Owner
        b3_date = date.today() + timedelta(days=60)
        b3 = Booking(
            booking_code="FM-2025-1150",
            customer_id=customer1.id,
            hall_id=hall1.id,
            package_id=wedding_pkg.id if wedding_pkg else None,
            event_date=b3_date,
            event_slot="Morning (8AM - 3PM)",
            expected_guests=450,
            event_type="Wedding / Vivaha Kalyanam",
            hall_rent=hall1.base_rent_price,
            package_cost=495000.0,
            catering_cost=200000.0,
            tax_amount=35000.0,
            total_amount=875000.0,
            advance_required=218750.0,
            advance_paid=0.0,
            balance_amount=875000.0,
            status="Pending Approval",
            food_choice="Pure Veg",
            notes="Requesting traditional South Indian banana leaf lunch seating."
        )
        db.session.add(b3)

        # Seed sample reviews
        r1 = Review(
            user_id=customer1.id,
            hall_id=hall1.id,
            booking_id=b1.id,
            rating=5,
            title="Magnificent traditional hall and exceptional hospitality!",
            comment="Hosted my sister's wedding at Sri Raja Rajeshwari Kalyana Mandapam. The central AC hall, mandap stage decor, chandelier illumination, and courteous management made the wedding unforgettable!",
            is_approved=True
        )
        db.session.add(r1)

        # Seed initial website settings & notifications
        notif1 = Notification(
            user_id=customer1.id,
            title="Welcome to Function Mall!",
            message="Explore our 10 event categories and discover the most luxurious halls for your special moments.",
            link="/categories"
        )
        db.session.add(notif1)

        # Website Settings
        settings = [
            ("site_name", "Function Mall"),
            ("contact_phone", "+91 91234 56789"),
            ("contact_email", "support@functionmall.com"),
            ("office_address", "Suite 701, Signature Horizon Towers, Road 36, Jubilee Hills, Hyderabad - 500033"),
            ("advance_hold_hours", "24"),
            ("tax_percentage", "18.0"),
            ("razorpay_key_id", "rzp_test_MallMockDemo2025")
        ]
        for k, v in settings:
            s = WebsiteSetting(key=k, value=v, description="Platform setting")
            db.session.add(s)

        db.session.commit()
        print("Database re-seeded successfully with verified indoor photos, Indian Hall names, and Owner credentials owner@checking.com / owner@123!")

if __name__ == '__main__':
    seed_database()
