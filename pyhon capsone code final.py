import mysql.connector as mycon
from mysql.connector import Error
from datetime import date

print("Program started")

try:
    print("Trying to connect...")
    mydb = mycon.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="root",
        database="movie",
        use_pure=True,
        connection_timeout=5
        )
    if mydb.is_connected():
        print("Connection successful")
        cur = mydb.cursor()

        # Automatically create movie_ratings table if not already present
        cur.execute("""
            CREATE TABLE IF NOT EXISTS movie_ratings (
                rating_id INT AUTO_INCREMENT PRIMARY KEY,
                movie_id INT,
                username VARCHAR(50),
                rating FLOAT,
                review VARCHAR(255),
                rating_date DATE
            )
        """)
        mydb.commit()

        # Automatically create users table for registration
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(100) NOT NULL,
                email VARCHAR(100),
                phone VARCHAR(15),
                registered_on DATE
            )
        """)
        mydb.commit()

except Error as e:
    print("Error:", e)


# ==========================================================
# PREDEFINED THEATRE, SCREEN & SEAT DATA
# ==========================================================

THEATRES = {
    "1": "PVR Cinemas - Grand Mall",
    "2": "INOX Multiplex - City Centre",
    "3": "Cinepolis - Downtown Galleria",
    "4": "Carnival Cinemas - Metro Square"
}

SCREENS = {
    "1": "Screen 1 - IMAX 3D (Dolby Atmos)",
    "2": "Screen 2 - 4DX (Motion & Effects)",
    "3": "Screen 3 - Audi 4K (Laser Projection)"
}

LANGUAGES = ["English", "Hindi", "Tamil", "Telugu", "Malayalam", "Kannada"]

# Valid passwords recognized for Staff/Admin accounts
STAFF_PASSWORDS = ["1234", "admin123", "staff123"]


# ==========================================================
# OTHER DEFAULT FEATURES
# ==========================================================

# Function to display movies
def show_movies():
    cur.execute("SELECT * FROM movie")
    print("\n" + "=" * 40)
    print("             MOVIE LIST")
    print("=" * 40)
    rows = cur.fetchall()
    if rows:
        print("Movie ID | Title | Show Time | Price | Date")
        print("-" * 40)
        for i in rows:
            print(i)
    else:
        print("No movies available in database.")
    print("=" * 40)


# Function to book ticket (with Theatre, Screen, Language & Seats)
def book_ticket(current_user="Guest"):
    try:
        show_movies()
        mid = int(input("\nEnter Movie ID to Book: "))

        # Fetch movie price and details
        cur.execute("SELECT price, movie_name FROM movie WHERE movie_id = %s", (mid,))
        row = cur.fetchone()

        if row is None:
            print("Invalid Movie ID")
            return

        base_price = row[0]
        movie_title = row[1]

        # 1. Feature: Booking Theatre Selection
        print("\n--- SELECT THEATRE ---")
        for k, v in THEATRES.items():
            print(f"{k}. {v}")
        t_choice = input("Choose Theatre (1-4): ").strip()
        selected_theatre = THEATRES.get(t_choice, "PVR Cinemas - Grand Mall")

        # 2. Feature: Booking Screen Selection
        print("\n--- SELECT SCREEN ---")
        for k, v in SCREENS.items():
            print(f"{k}. {v}")
        s_choice = input("Choose Screen (1-3): ").strip()
        selected_screen = SCREENS.get(s_choice, "Screen 1 - IMAX 3D")

        # 3. Feature: Language Selection
        print("\n--- SELECT MOVIE LANGUAGE ---")
        for idx, lang in enumerate(LANGUAGES, 1):
            print(f"{idx}. {lang}")
        l_choice = input("Choose Language (1-6): ").strip()
        try:
            selected_language = LANGUAGES[int(l_choice) - 1]
        except (ValueError, IndexError):
            selected_language = "English"

        # 4. Feature: Seat Details & Category Selection
        show_seat_details()
        print("\n--- SELECT SEAT TIER ---")
        print("1. Silver (Standard Price)")
        print("2. Gold (+Rs. 50 per ticket)")
        print("3. Platinum / VIP (+Rs. 100 per ticket)")
        tier_choice = input("Choose Tier (1-3): ").strip()

        tier_extra = 0
        tier_name = "Silver"
        if tier_choice == "2":
            tier_extra = 50
            tier_name = "Gold"
        elif tier_choice == "3":
            tier_extra = 100
            tier_name = "Platinum VIP"

        t = int(input("\nEnter number of tickets: "))
        if t <= 0:
            print("Ticket count must be greater than 0")
            return

        seat_numbers = input("Enter Seat Numbers (e.g. A1, A2 or D5): ").strip()

        bid = int(input("Enter New Booking ID: "))

        price_per_ticket = base_price + tier_extra
        total = price_per_ticket * t
        b_date = date.today()

        cur.execute(
            """
            INSERT INTO booking
            (booking_id, movie_id, tickets, total_amount, movie_date)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (bid, mid, t, total, b_date)
        )

        mydb.commit()

        # Display booking confirmation ticket
        print("\n" + "=" * 45)
        print("         BOOKING CONFIRMED!")
        print("=" * 45)
        print("Booking ID   :", bid)
        print("Customer     :", current_user)
        print("Movie        :", movie_title)
        print("Theatre      :", selected_theatre)
        print("Screen       :", selected_screen)
        print("Language     :", selected_language)
        print("Seat Tier    :", tier_name)
        print("Seat No(s)   :", seat_numbers)
        print("Tickets      :", t)
        print("Booking Date :", b_date)
        print("Total Amount : Rs.", total)
        print("=" * 45)

    except ValueError:
        print("Invalid numeric input")

    except mycon.IntegrityError:
        print("Booking ID already exists! Please use a unique Booking ID.")

    except Error as e:
        print("Database error:", e)


# Add movie
def add_movie():
    try:
        mid = int(input("Enter Movie ID: "))
        name = input("Enter Movie Name: ")
        time = input("Enter Show Time: ")
        price = int(input("Enter Ticket Price: "))
        m_date = input("Enter Movie Date (YYYY-MM-DD): ")

        cur.execute(
            "INSERT INTO movie VALUES (%s, %s, %s, %s, %s)",
            (mid, name, time, price, m_date)
        )

        mydb.commit()
        print("Movie added successfully")

    except mycon.IntegrityError:
        print("Movie ID already exists")

    except ValueError:
        print("Invalid input")


# Search movie (with ID, Name, and Language options)
def search_movie():
    print("\n--- SEARCH MOVIES ---")
    print("1. Search by Movie ID")
    print("2. Search by Movie Name")
    print("3. Search by Movie Language")
    
    ch = input("Enter choice: ").strip()

    if ch == "1":
        mid = int(input("Enter Movie ID: "))
        cur.execute("SELECT * FROM movie WHERE movie_id=%s", (mid,))
        row = cur.fetchone()
        if row:
            print("Movie Found:", row)
        else:
            print("Movie not found")
        
    elif ch == "2":
        name = input("Enter Movie Name: ")
        cur.execute("SELECT * FROM movie WHERE movie_name LIKE %s", ('%' + name + '%',))
        rows = cur.fetchall()
        if rows:
            print("\nMovies Found:")
            for r in rows:
                print(r)
        else:
            print("No movies matched your search.")

    elif ch == "3":
        print("\nSupported Languages:")
        for idx, lang in enumerate(LANGUAGES, 1):
            print(f"{idx}. {lang}")
        l_ch = input("Select Language (1-6): ").strip()
        try:
            chosen_lang = LANGUAGES[int(l_ch) - 1]
            print(f"\nSearching movies available in {chosen_lang} audio tracks...")
            cur.execute("SELECT * FROM movie")
            rows = cur.fetchall()
            if rows:
                for r in rows:
                    print(r, f"| Available in: {chosen_lang}")
            else:
                print("No movies found.")
        except (ValueError, IndexError):
            print("Invalid language selection")
        
    else:
        print("Invalid choice")


# To show bookings
def show_bookings():
    cur.execute("SELECT * FROM booking")
    rows = cur.fetchall()
    if rows:
        print("\n--- ALL BOOKINGS ---")
        print("Booking ID | Movie ID | Tickets | Total Amount | Date")
        print("-" * 45)
        for r in rows:
            print(r)
    else:
        print("No bookings found")

        
# To update price
def update_price():
    try:
        mid = int(input("Enter Movie ID: "))
        new_price = int(input("Enter New Price: "))
        cur.execute(
            "UPDATE movie SET price=%s WHERE movie_id=%s",
            (new_price, mid)
        )
        if cur.rowcount == 0:
            print("Movie ID not found")
        else:
            mydb.commit()
            print("Price updated successfully")
    except ValueError:
        print("Invalid numeric input")

        
# To delete movies
def delete_movie():
    try:
        mid = int(input("Enter Movie ID to delete: "))

        # Check bookings
        cur.execute(
            "SELECT COUNT(*) FROM booking WHERE movie_id=%s",
            (mid,)
        )

        count = cur.fetchone()[0]

        if count > 0:
            print("\nCannot delete this movie!")
            print("This movie has", count, "booking(s).")
            print("Cancel the bookings first.")
            return

        # Delete ratings and reviews
        cur.execute(
            "DELETE FROM movie_ratings WHERE movie_id=%s",
            (mid,)
        )

        # Delete movie
        cur.execute(
            "DELETE FROM movie WHERE movie_id=%s",
            (mid,)
        )

        mydb.commit()

        print("Movie deleted successfully")

    except ValueError:
        print("Invalid numeric input")

    except Error as e:
        mydb.rollback()
        print("Database error:", e)

# Search movies by price
def search_by_price():
    try:
        low = int(input("Enter minimum price: "))
        high = int(input("Enter maximum price: "))
        cur.execute(
            "SELECT * FROM movie WHERE price BETWEEN %s AND %s",
            (low, high)
        )
        rows = cur.fetchall()
        if rows:
            print(f"\n--- MOVIES BETWEEN Rs. {low} AND Rs. {high} ---")
            for r in rows:
                print(r)
        else:
            print("No movies found in this price range")
    except ValueError:
        print("Invalid numeric input")


# Count bookings
def count_movie_bookings():
    try:
        mid = int(input("Enter Movie ID to check bookings: "))
        cur.execute(
            "SELECT COUNT(*) FROM booking WHERE movie_id = %s",
            (mid,)
        )
        count = cur.fetchone()[0]
        print("Total number of bookings for this movie:", count)
    except ValueError:
        print("Invalid numeric input")


# Most watched movie
def most_watched_movie():
    cur.execute("""
        SELECT movie.movie_id, movie.movie_name, COUNT(booking.movie_id) AS total_bookings
        FROM booking
        JOIN movie ON booking.movie_id = movie.movie_id
        GROUP BY booking.movie_id
        ORDER BY total_bookings DESC
        LIMIT 1
    """)
    row = cur.fetchone()
    if row:
        print("\n--- Most Watched Movie Details ---")
        print("Movie ID:", row[0])
        print("Movie Name:", row[1])
        print("Total Bookings:", row[2])
    else:
        print("No bookings found")


# Top 3 movies
def top_3_movies():
    cur.execute("""
        SELECT movie.movie_id, movie.movie_name, COUNT(booking.movie_id) AS total_bookings
        FROM booking
        JOIN movie ON booking.movie_id = movie.movie_id
        GROUP BY booking.movie_id
        ORDER BY total_bookings DESC
        LIMIT 3
    """)
    rows = cur.fetchall()
    if rows:
        print("\n--- Top 3 Most Watched Movies ---")
        for r in rows:
            print("Movie ID:", r[0], "| Movie Name:", r[1], "| Bookings:", r[2])
    else:
        print("No bookings found")

        
# Canceling a booking
def cancel_booking():
    try:
        bid = int(input("Enter Booking ID to cancel: "))
        cur.execute("DELETE FROM booking WHERE booking_id = %s", (bid,))
        if cur.rowcount == 0:
            print("Booking ID not found")
        else:
            mydb.commit()
            print("Booking cancelled successfully")
    except ValueError:
        print("Invalid numeric input")

        
# To show snacks menu
def show_snacks():
    cur.execute("SELECT * FROM snacks")
    print("\n--- SNACKS MENU ---")
    print("Snack ID | Snack Name | Price")
    for row in cur:
        print(row)


# Order snacks for a booking
def order_snacks():
    try:
        show_snacks()
        bid = int(input("\nEnter Booking ID: "))
        sid = int(input("Enter Snack ID: "))
        qty = int(input("Enter Quantity: "))

        # Check snack price
        cur.execute("SELECT price FROM snacks WHERE snack_id=%s", (sid,))
        row = cur.fetchone()
        if row is None:
            print("Invalid Snack ID")
            return

        price = row[0]
        total = price * qty

        cur.execute(
            "INSERT INTO snacks_order VALUES (%s, %s, %s, %s)",
            (bid, sid, qty, total)
        )
        mydb.commit()
        print("Snack ordered successfully")
        print("Total snack cost =", total)
    except ValueError:
        print("Invalid input")
    except mycon.IntegrityError:
        print("Booking ID or order error")
    except Error as e:
        print("Database error:", e)


# Show Snacks Ordered for a Booking    
def show_snack_bill():
    try:
        bid = int(input("Enter Booking ID: "))
        cur.execute("""
            SELECT s.snack_name, so.qty, so.total_cost
            FROM snacks_order so
            JOIN snacks s ON so.snack_id = s.snack_id
            WHERE so.booking_id = %s
        """, (bid,))

        rows = cur.fetchall()
        if not rows:
            print("No snacks ordered for this booking")
            return

        print("\n--- SNACK BILL ---")
        print("Snack | Qty | Cost")
        for r in rows:
            print(r)
    except ValueError:
        print("Invalid numeric input")

    
# Total Snacks Amount for a Booking
def total_snack_amount():
    try:
        bid = int(input("Enter Booking ID: "))
        cur.execute(
            "SELECT SUM(total_cost) FROM snacks_order WHERE booking_id=%s",
            (bid,)
        )
        total = cur.fetchone()[0]

        if total is None:
            print("No snacks ordered for this booking")
        else:
            print("Total Snack Amount =", total)
    except ValueError:
        print("Invalid numeric input")

        
# Most Ordered Snack
def most_ordered_snack():
    cur.execute("""
        SELECT s.snack_name, SUM(so.qty) AS total_qty
        FROM snacks_order so
        JOIN snacks s ON so.snack_id = s.snack_id
        GROUP BY so.snack_id
        ORDER BY total_qty DESC
        LIMIT 1
    """)
    row = cur.fetchone()
    if row:
        print("\n--- MOST ORDERED SNACK ---")
        print("Most Ordered Snack:", row[0], f"(Total Quantity: {row[1]})")
    else:
        print("No snack orders found")


# Combined Bill (Movie + Snacks)
def full_bill():
    try:
        bid = int(input("Enter Booking ID: "))

        cur.execute("SELECT total_amount FROM booking WHERE booking_id=%s", (bid,))
        movie = cur.fetchone()

        if movie is None:
            print("Invalid Booking ID")
            return

        cur.execute("SELECT SUM(total_cost) FROM snacks_order WHERE booking_id=%s", (bid,))
        snacks = cur.fetchone()[0]

        snacks = snacks if snacks else 0
        print("\n" + "=" * 35)
        print("         COMBINED BILL")
        print("=" * 35)
        print("Booking ID   :", bid)
        print("Movie Cost   :", movie[0])
        print("Snacks Cost  :", snacks)
        print("-" * 35)
        print("Grand Total  :", movie[0] + snacks)
        print("=" * 35)
    except ValueError:
        print("Invalid numeric input")


# ==========================================================
# NEW FEATURES: SEAT DETAILS, THEATRES, SCREENS & RATINGS
# ==========================================================

# Feature 3: Seat Details & Layout
def show_seat_details():
    print("\n" + "=" * 48)
    print("               THEATRE SEAT LAYOUT")
    print("=" * 48)
    print("                  [ SCREEN THIS WAY ]")
    print("-" * 48)
    print("SILVER TIER (Standard Price):")
    print("  Row A: [A1] [A2] [A3] [A4] [A5]   [A6] [A7] [A8] [A9] [A10]")
    print("  Row B: [B1] [B2] [B3] [B4] [B5]   [B6] [B7] [B8] [B9] [B10]")
    print("  Row C: [C1] [C2] [C3] [C4] [C5]   [C6] [C7] [C8] [C9] [C10]")
    print("-" * 48)
    print("GOLD TIER (+ Rs. 50):")
    print("  Row D: [D1] [D2] [D3] [D4] [D5]   [D6] [D7] [D8] [D9] [D10]")
    print("  Row E: [E1] [E2] [E3] [E4] [E5]   [E6] [E7] [E8] [E9] [E10]")
    print("  Row F: [F1] [F2] [F3] [F4] [F5]   [F6] [F7] [F8] [F9] [F10]")
    print("-" * 48)
    print("PLATINUM / VIP RECLINERS (+ Rs. 100):")
    print("  Row G: [G1] [G2] [G3] [G4]         [G5] [G6] [G7] [G8]")
    print("  Row H: [H1] [H2] [H3] [H4]         [H5] [H6] [H7] [H8]")
    print("=" * 48)


# Feature 4 & 5: View Theatres & Screens
def show_theatres_and_screens():
    print("\n" + "=" * 48)
    print("         AVAILABLE THEATRES & SCREENS")
    print("=" * 48)
    print("THEATRES:")
    for k, v in THEATRES.items():
        print(f"  {k}. {v}")
    print("\nSCREENS & FORMATS:")
    for k, v in SCREENS.items():
        print(f"  {k}. {v}")
    print("=" * 48)


# Feature 7: Rate a Movie (Customer)
def rate_movie(username="Customer"):
    try:
        show_movies()
        mid = int(input("\nEnter Movie ID to rate: "))
        
        cur.execute("SELECT movie_name FROM movie WHERE movie_id = %s", (mid,))
        row = cur.fetchone()
        if not row:
            print("Invalid Movie ID")
            return
            
        movie_name = row[0]
        rating = float(input(f"Enter your rating for '{movie_name}' (1.0 to 5.0 stars): "))
        if rating < 1.0 or rating > 5.0:
            print("Rating must be between 1.0 and 5.0")
            return
            
        review = input("Enter a short review / comment: ").strip()
        r_date = date.today()

        cur.execute(
            """
            INSERT INTO movie_ratings (movie_id, username, rating, review, rating_date)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (mid, username, rating, review, r_date)
        )
        mydb.commit()
        print(f"\nThank you {username}! Your rating ({rating}/5.0) for '{movie_name}' was recorded.")
        
    except ValueError:
        print("Invalid input! Please enter a valid number.")
    except Error as e:
        print("Database error:", e)


# Feature 7: View Movie Ratings & Reviews
def show_movie_ratings():
    try:
        print("\n" + "=" * 45)
        print("            MOVIE RATINGS & REVIEWS")
        print("=" * 45)
        cur.execute("""
            SELECT m.movie_name, AVG(r.rating) AS avg_rating, COUNT(r.rating_id) AS total_reviews
            FROM movie m
            LEFT JOIN movie_ratings r ON m.movie_id = r.movie_id
            GROUP BY m.movie_id, m.movie_name
        """)
        summary = cur.fetchall()
        print("Movie Name | Average Rating | Total Reviews")
        print("-" * 45)
        for s in summary:
            avg_score = f"{round(s[1], 1)} / 5.0" if s[1] is not None else "No ratings yet"
            print(f"{s[0]} | {avg_score} | {s[2]} reviews")
            
        print("\nRecent User Reviews:")
        print("-" * 45)
        cur.execute("""
            SELECT m.movie_name, r.username, r.rating, r.review, r.rating_date
            FROM movie_ratings r
            JOIN movie m ON r.movie_id = m.movie_id
            ORDER BY r.rating_id DESC
            LIMIT 5
        """)
        reviews = cur.fetchall()
        if reviews:
            for rev in reviews:
                print(f"[{rev[0]}] Rated {rev[2]}/5 by {rev[1]} on {rev[4]}: \"{rev[3]}\"")
        else:
            print("No written reviews submitted yet.")
        print("=" * 45)
    except Error as e:
        print("Database error:", e)


# ==========================================================
# SECTION 0: USER REGISTRATION
# ==========================================================

def user_register():
    """
    Registration Portal: Allows a new customer to create an account.
    Stores user details in the 'users' table.
    """
    print("\n" + "=" * 45)
    print("          NEW USER REGISTRATION")
    print("=" * 45)

    username = input("Enter a Username: ").strip()
    if not username:
        print("\n>>> [ERROR] Username cannot be empty! <<<")
        return False

    # Check if username already exists
    try:
        cur.execute("SELECT username FROM users WHERE username = %s", (username,))
        if cur.fetchone():
            print(f"\n>>> [ERROR] Username '{username}' is already taken. Please choose another. <<<")
            return False
    except Error as e:
        print("Database error:", e)
        return False

    password = input("Enter Password: ").strip()
    if not password or len(password) < 4:
        print("\n>>> [ERROR] Password must be at least 4 characters! <<<")
        return False

    confirm_pass = input("Confirm Password: ").strip()
    if password != confirm_pass:
        print("\n>>> [ERROR] Passwords do not match! <<<")
        return False

    email = input("Enter Email Address (optional, press Enter to skip): ").strip()
    phone = input("Enter Phone Number (optional, press Enter to skip): ").strip()
    if phone and (not phone.isdigit() or len(phone) < 10):
        print("\n>>> [ERROR] Invalid phone number. Must be at least 10 digits! <<<")
        return False

    reg_date = date.today()

    try:
        cur.execute(
            """
            INSERT INTO users (username, password, email, phone, registered_on)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (username, password, email if email else None, phone if phone else None, reg_date)
        )
        mydb.commit()
        print("\n" + "=" * 45)
        print("      REGISTRATION SUCCESSFUL!")
        print("=" * 45)
        print(f"  Welcome, {username}!")
        print(f"  Account created on: {reg_date}")
        print("  You can now log in using your credentials.")
        print("=" * 45)
        return True

    except mycon.IntegrityError:
        print(f"\n>>> [ERROR] Username '{username}' already exists! <<<")
        return False
    except Error as e:
        print("Database error:", e)
        return False


# ==========================================================
# SECTIONS 1 & 2: THEATRE STAFF LOGIN & USER LOGIN
# ==========================================================

def staff_login():
    """
    Feature 1: Dedicated Theatre Staff Login
    """
    print("\n" + "=" * 45)
    print("           THEATRE STAFF LOGIN")
    print("=" * 45)
    username = input("Enter Staff ID / Username: ").strip()
    password = input("Enter Staff Password: ").strip()

    if ("staff" in username.lower() or "admin" in username.lower()) and password in STAFF_PASSWORDS:
        print(f"\n>>> Staff Login Successful! Welcome [{username}] <<<")
        return username
    else:
        print("\n>>> [ERROR] Invalid Staff ID or Password! Access Denied. <<<")
        return None


def user_login():
    """
    Feature 2: Dedicated User / Customer Login
    Validates credentials against the 'users' table.
    """
    print("\n" + "=" * 45)
    print("            USER / CUSTOMER LOGIN")
    print("=" * 45)
    username = input("Enter Your Username: ").strip()
    password = input("Enter Password: ").strip()

    if not username or not password:
        print("\n>>> [ERROR] Username and password cannot be empty! <<<")
        return None

    try:
        cur.execute(
            "SELECT username FROM users WHERE username = %s AND password = %s",
            (username, password)
        )
        row = cur.fetchone()
        if row:
            print(f"\n>>> Login Successful! Welcome Customer [{username}] <<<")
            return username
        else:
            print("\n>>> [ERROR] Invalid username or password! <<<")
            print("    Tip: If you are new, please register first (Option 1 on Main Menu).")
            return None
    except Error as e:
        print("Database error:", e)
        return None


# ==========================================================
# STAFF PORTAL (Administrative Operations)
# ==========================================================

def staff_portal(staff_user):
    """
    Staff Portal containing administrative and movie-management functions.
    """
    while True:
        print("\n" + "=" * 45)
        print(f"          THEATRE STAFF PORTAL ({staff_user})")
        print("=" * 45)
        print("1.  Show Movies")
        print("2.  Add Movie")
        print("3.  Search Movie (ID / Name / Language)")
        print("4.  View Bookings")
        print("5.  Update Movie Price")
        print("6.  Delete Movie")
        print("7.  Search Movies by Price")
        print("8.  Count Bookings for a Movie")
        print("9.  Show Most Watched Movie")
        print("10. Show Top 3 Most Watched Movies")
        print("11. View Seat Details & Layout")
        print("12. View Theatres & Screens")
        print("13. View Movie Ratings & Reviews")
        print("14. Show Most Ordered Snack")
        print("15. Logout to Main Menu")
        print("=" * 45)
        
        ch = input("Enter choice (1-15): ").strip()

        if ch == "1":
            show_movies()
        elif ch == "2":
            add_movie()
        elif ch == "3":
            search_movie()
        elif ch == "4":
            show_bookings()
        elif ch == "5":
            update_price()
        elif ch == "6":
            delete_movie()
        elif ch == "7":
            search_by_price()
        elif ch == "8":
            count_movie_bookings()
        elif ch == "9":
            most_watched_movie()
        elif ch == "10":
            top_3_movies()
        elif ch == "11":
            show_seat_details()
        elif ch == "12":
            show_theatres_and_screens()
        elif ch == "13":
            show_movie_ratings()
        elif ch == "14":
            most_ordered_snack()
        elif ch == "15":
            print("\nLogging out from Staff Portal...")
            break
        else:
            print("Invalid choice! Please enter a valid option (1-15).")


# ==========================================================
# USER PORTAL (Customer Operations)
# ==========================================================

def user_portal(current_user):
    """
    User Portal containing customer booking, screen/seat selection and snack operations.
    """
    while True:
        print("\n" + "=" * 45)
        print(f"            USER PORTAL ({current_user})")
        print("=" * 45)
        print("1.  Show Movies")
        print("2.  Search Movie (ID / Name / Language)")
        print("3.  View Seat Details & Layout")
        print("4.  View Theatres & Screens")
        print("5.  Book Ticket (Theatre + Screen + Language + Seat)")
        print("6.  Cancel Booking")
        print("7.  Rate a Movie & Give Review")
        print("8.  View Movie Ratings & Reviews")
        print("9.  Order Snacks")
        print("10. Show Snack Bill")
        print("11. Show Total Snack Amount")
        print("12. Show Most Ordered Snack")
        print("13. Combined Bill (Movie + Snacks)")
        print("14. Logout to Main Menu")
        print("=" * 45)
        
        ch = input("Enter choice (1-14): ").strip()

        if ch == "1":
            show_movies()
        elif ch == "2":
            search_movie()
        elif ch == "3":
            show_seat_details()
        elif ch == "4":
            show_theatres_and_screens()
        elif ch == "5":
            book_ticket(current_user)
        elif ch == "6":
            cancel_booking()
        elif ch == "7":
            rate_movie(current_user)
        elif ch == "8":
            show_movie_ratings()
        elif ch == "9":
            order_snacks()
        elif ch == "10":
            show_snack_bill()
        elif ch == "11":
            total_snack_amount()
        elif ch == "12":
            most_ordered_snack()
        elif ch == "13":
            full_bill()
        elif ch == "14":
            print("\nLogging out from User Portal...")
            break
        else:
            print("Invalid choice! Please enter a valid option (1-14).")


# ==========================================================
# MAIN PROGRAM ENTRY POINT & LOGIN SELECTION
# ==========================================================

if 'mydb' in globals() and mydb.is_connected():
    while True:
        print("\n" + "=" * 48)
        print("         MOVIE TICKET BOOKING SYSTEM")
        print("=" * 48)
        print("  1. Register (New User)")
        print("  2. Theatre Staff Login")
        print("  3. User / Customer Login")
        print("  4. Exit Program")
        print("=" * 48)
        
        choice = input("Enter your choice (1-4): ").strip()

        if choice == "1":
            user_register()

        elif choice == "2":
            staff_user = staff_login()
            if staff_user:
                staff_portal(staff_user)

        elif choice == "3":
            user = user_login()
            if user:
                user_portal(user)

        elif choice == "4" or choice.lower() == "exit":
            print("\nThank you for using Movie Ticket Booking System. Goodbye!")
            break

        else:
            print("Invalid choice! Please select 1, 2, 3, or 4.")

    # Cleanly close database connection on exit
    cur.close()
    mydb.close()
    print("Database connection closed.")
else:
    print("Unable to start system due to database connection error.")
