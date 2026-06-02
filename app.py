# Langkah 1: Impor semua library yang dibutuhkan
import psycopg2
import psycopg2.extras
from flask import Flask, render_template, abort, url_for

# Langkah 2: Buat aplikasi Flask.
app = Flask(__name__)

# Langkah 3: Konfigurasi koneksi ke database Anda
# GANTI DENGAN DETAIL KONEKSI ANDA YANG SEBENARNYA
DB_CONFIG = {
    "host": "localhost",
    "dbname": "toko_mebel",
    "user": "postgres",
    "password": "postgres"  # GANTI DENGAN PASSWORD ANDA JIKA BERBEDA
}

# Definisikan fungsi bantuan untuk membuat koneksi
def get_db_connection():
    """Membuka koneksi baru ke database."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.OperationalError as e:
        print(f"Error connecting to database: {e}")
        return None

# Definisikan route untuk Halaman Utama ('/')
@app.route('/')
def home():
    """Menampilkan halaman utama dengan daftar semua merek."""
    conn = get_db_connection()
    if conn is None:
        return "<h1>Error: Tidak dapat terhubung ke database.</h1>", 500

    cur = None
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT name, image_url FROM brands ORDER BY name;")
        brands = cur.fetchall()
    except Exception as e:
        print(f"Error saat query ke database: {e}")
        return "<h1>Error: Gagal mengambil data dari database.</h1>", 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

    return render_template('index.html', brands=brands)

# Definisikan route untuk Halaman Detail Merek
@app.route('/brand/<string:brand_name>')
def brand_page(brand_name):
    """Menampilkan halaman detail untuk sebuah merek beserta produknya."""
    conn = get_db_connection()
    if conn is None:
        return "<h1>Error: Tidak dapat terhubung ke database.</h1>", 500
        
    cur = None
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        cur.execute("SELECT hero_image_url FROM brands WHERE name = %s;", (brand_name,))
        brand_info = cur.fetchone()

        if brand_info is None:
            abort(404, description=f"Merek '{brand_name}' tidak ditemukan.")

        query = """
            SELECT m.name, m.price_range, m.description, m.image_url, m.ecommerce_url 
            FROM mattresses AS m
            JOIN brands AS b ON m.brand_id = b.id
            WHERE b.name = %s;
        """
        cur.execute(query, (brand_name,))
        mattresses = cur.fetchall()
    except Exception as e:
        print(f"Error saat query ke database: {e}")
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

# Bagian PALING PENTING untuk menjalankan server
if __name__ == '__main__':
    app.run(debug=True)