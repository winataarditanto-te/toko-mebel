# =========================
# IMPORT LIBRARY
# =========================
import os
import psycopg2
import psycopg2.extras
from urllib.parse import urlparse
from flask import Flask, render_template, abort

# =========================
# FLASK APP
# =========================
app = Flask(__name__)

# =========================
# DATABASE CONNECTION (FIXED FOR RAILWAY)
# =========================
def get_db_connection():
    """Koneksi ke PostgreSQL Railway menggunakan DATABASE_URL"""
    try:
        # DEBUG: cek apakah variable masuk
        print("DATABASE_URL =", os.environ.get("DATABASE_URL"))

        DATABASE_URL = os.environ.get("DATABASE_URL")

        if not DATABASE_URL:
            raise Exception("DATABASE_URL belum masuk ke environment Railway!")

        result = urlparse(DATABASE_URL)

        conn = psycopg2.connect(
            dbname=result.path[1:],
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port
        )
        return conn

    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

# =========================
# HOME PAGE
# =========================
@app.route('/')
def home():
    conn = get_db_connection()
    if conn is None:
        return "<h1>Error: Tidak dapat terhubung ke database.</h1>", 500

    cur = None
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT name, image_url FROM brands ORDER BY name;")
        brands = cur.fetchall()

    except Exception as e:
        print(f"Error query database: {e}")
        return "<h1>Error: Gagal mengambil data dari database.</h1>", 500

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

    return render_template('index.html', brands=brands)


# =========================
# BRAND DETAIL PAGE
# =========================
@app.route('/brand/<string:brand_name>')
def brand_page(brand_name):
    conn = get_db_connection()
    if conn is None:
        return "<h1>Error: Tidak dapat terhubung ke database.</h1>", 500

    cur = None
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # ambil hero image brand
        cur.execute(
            "SELECT hero_image_url FROM brands WHERE name = %s;",
            (brand_name,)
        )
        brand_info = cur.fetchone()

        if brand_info is None:
            abort(404, description="Brand tidak ditemukan")

        # ambil produk
        query = """
            SELECT m.name, m.price_range, m.description, m.image_url, m.ecommerce_url
            FROM mattresses AS m
            JOIN brands AS b ON m.brand_id = b.id
            WHERE b.name = %s;
        """
        cur.execute(query, (brand_name,))
        mattresses = cur.fetchall()

    except Exception as e:
        print(f"Error query database: {e}")
        return "<h1>Error: Gagal mengambil data dari database.</h1>", 500

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

    return render_template(
        'brand_detail.html',
        mattresses=mattresses,
        brand_name=brand_name,
        hero_image=brand_info['hero_image_url']
    )


# =========================
# RUN SERVER
# =========================
if __name__ == '__main__':
    app.run(debug=True)