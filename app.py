import streamlit as st
import re
import io
import json
from datetime import datetime, date
from PIL import Image, ImageOps
import gspread
from google.oauth2.service_account import Credentials

# ============================================================
# KONFIGURASI HALAMAN
# ============================================================
st.set_page_config(
    page_title="INTIF — Form Pengisian ID",
    page_icon="🛂",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ============================================================
# CSS
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --navy:   #0B1F3A;
    --gold:   #C9A84C;
    --gold2:  #E8C97A;
    --cream:  #F7F4EE;
    --white:  #FFFFFF;
    --red:    #C0392B;
    --green:  #1A7A4A;
    --blue:   #1A4A7A;
    --border: #D6CEBD;
    --shadow: 0 4px 24px rgba(11,31,58,0.10);
}
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--cream);
    color: var(--navy);
}
.intif-header {
    background: linear-gradient(135deg, var(--navy) 0%, #163660 100%);
    color: var(--white);
    border-radius: 16px;
    padding: 28px 32px 24px 32px;
    margin-bottom: 24px;
    border-left: 5px solid var(--gold);
    box-shadow: var(--shadow);
    position: relative;
    overflow: hidden;
}
.intif-header::after {
    content: '';
    position: absolute;
    right: -30px; top: -30px;
    width: 130px; height: 130px;
    border-radius: 50%;
    border: 30px solid rgba(201,168,76,0.10);
}
.intif-header h1 {
    font-family: 'Playfair Display', serif;
    font-size: 1.45rem;
    margin: 0 0 4px 0;
    color: var(--gold2);
}
.intif-header p { margin: 0; font-size: 0.82rem; opacity: 0.80; }
.badge {
    display: inline-block;
    background: var(--gold); color: var(--navy);
    font-size: 0.65rem; font-weight: 700;
    letter-spacing: 1.5px; text-transform: uppercase;
    padding: 3px 10px; border-radius: 20px; margin-bottom: 8px;
}
.card {
    background: var(--white); border-radius: 14px;
    padding: 24px 24px 20px 24px; margin-bottom: 16px;
    box-shadow: var(--shadow); border: 1px solid var(--border);
}
.card-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.05rem; font-weight: 600;
    color: var(--navy); margin-bottom: 4px;
}
.card-sub { font-size: 0.78rem; color: #6b7588; margin-bottom: 14px; }
.section-label {
    font-size: 0.72rem; font-weight: 700;
    letter-spacing: 1.5px; text-transform: uppercase;
    color: var(--gold); margin: 18px 0 10px 0;
    padding-bottom: 6px;
    border-bottom: 1px solid var(--border);
}
.steps-wrap {
    display: flex; align-items: center;
    margin-bottom: 24px; gap: 0;
}
.step-item {
    flex: 1; text-align: center;
    font-size: 0.65rem; font-weight: 600;
    color: #a0a8b8; letter-spacing: 0.3px;
    text-transform: uppercase; padding-top: 6px;
}
.step-item.active { color: var(--navy); }
.step-item.done   { color: var(--green); }
.step-dot {
    width: 26px; height: 26px; border-radius: 50%;
    background: #e3e7ef;
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto 5px auto;
    font-size: 0.72rem; font-weight: 700;
    color: #a0a8b8; border: 2px solid #e3e7ef;
}
.step-item.active .step-dot {
    background: var(--navy); color: var(--white);
    border-color: var(--navy);
    box-shadow: 0 0 0 3px rgba(11,31,58,0.12);
}
.step-item.done .step-dot {
    background: var(--green); color: var(--white);
    border-color: var(--green);
}
.alert-danger {
    background: #FFF0EE; border-left: 4px solid var(--red);
    border-radius: 10px; padding: 12px 16px; margin-bottom: 12px;
    color: var(--red); font-size: 0.85rem; font-weight: 500; line-height: 1.55;
}
.alert-warning {
    background: #FFFBEE; border-left: 4px solid var(--gold);
    border-radius: 10px; padding: 12px 16px; margin-bottom: 12px;
    color: #7a5c00; font-size: 0.85rem; font-weight: 500; line-height: 1.55;
}
.alert-success {
    background: #EAF7EF; border-left: 4px solid var(--green);
    border-radius: 10px; padding: 12px 16px; margin-bottom: 12px;
    color: var(--green); font-size: 0.85rem; font-weight: 500;
}
.stButton > button {
    background: linear-gradient(135deg, var(--navy) 0%, #163660 100%) !important;
    color: var(--white) !important; border: none !important;
    border-radius: 10px !important; font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important; font-size: 0.90rem !important;
    padding: 11px 24px !important; width: 100% !important;
    box-shadow: 0 3px 12px rgba(11,31,58,0.18) !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.88 !important; }
[data-testid="stFileUploader"] {
    border: 2px dashed var(--border) !important;
    border-radius: 12px !important; background: #FAFAF8 !important;
}
.stTextInput > div > div > input,
.stSelectbox > div > div > div,
.stTextArea textarea {
    border-radius: 8px !important;
    border: 1.5px solid var(--border) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.88rem !important;
    color: var(--navy) !important;
    background: #FAFAF8 !important;
}
label[data-testid="stWidgetLabel"] {
    font-size: 0.75rem !important; font-weight: 600 !important;
    letter-spacing: 0.3px !important; color: #4a5568 !important;
    text-transform: uppercase !important;
}
.confirm-table { width: 100%; border-collapse: collapse; font-size: 0.82rem; }
.confirm-table td { padding: 7px 12px; border-bottom: 1px solid #f0ece4; }
.confirm-table td:first-child { color: #6b7588; font-weight: 600; width: 45%; }
.confirm-table td:last-child { color: var(--navy); font-weight: 500; }
.confirm-section { font-weight: 700; color: var(--navy);
    background: #f7f4ee; padding: 8px 12px;
    font-size: 0.75rem; letter-spacing: 1px; text-transform: uppercase; }
hr { border-color: var(--border) !important; margin: 16px 0 !important; }
.footer {
    text-align: center; font-size: 0.72rem; color: #9aa3b2;
    margin-top: 28px; padding-bottom: 16px; line-height: 1.7;
}
@keyframes fadeIn {
    from { opacity:0; transform:translateY(10px); }
    to   { opacity:1; transform:translateY(0); }
}
.fade-in { animation: fadeIn 0.4s ease; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# GOOGLE SHEETS
# ============================================================
SHEET_NAME = "Form pengisian ID Intif"
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

HEADERS = [
    # a. OCR Paspor Baru
    "NAMA LENGKAP", "NOMOR PASPOR", "KANTOR PENERBIT PASPOR",
    "TANGGAL TERBIT PASPOR", "TANGGAL HABIS BERLAKU PASPOR",
    "KOTA KELAHIRAN", "TANGGAL LAHIR",
    # b. Data tambahan
    "SIJIL", "SAFHAH", "KEKELUARGAAN",
    # c. OCR Paspor Lama
    "NO PASPOR LAMA", "KANTOR PENERBIT PASPOR LAMA",
    "TGL TERBIT PASPOR LAMA", "TGL HABIS PASPOR LAMA",
    # d. Data diri
    "JENIS KELAMIN", "ID KK", "STATUS KK", "TAHUN KEDATANGAN",
    "NAMA SMA/PONDOK/SEDERAJAT", "NAMA ARAB", "TENTANG ANDA", "CATATAN KHUSUS",
    # e. Pemisah
    "-",
    # f. Pendidikan
    "LEMBAGA PENDIDIKAN", "FAKULTAS", "JURUSAN", "TINGKAT/KELAS", "TAHUN AJARAN",
    # g. Pemisah
    "--",
    # h. Alamat
    "AREA", "NO. IMARAH", "LANTAI", "NO. SYAQQAH",
    "NAMA JALAN", "DISTRIK", "KAWASAN", "PROVINSI",
    # i. Pemisah
    "---",
    # j. Kontak
    "NOMOR TELEPON", "NOMOR WHATSAPP", "EMAIL ADDRESS", "SUREL",
    "FACEBOOK", "INSTAGRAM", "TWITTER",
    "NOMOR TELEPON TEMAN RUMAH", "NOMOR TELEPON DARURAT",
    "NOMOR TELEPON DARURAT LAINNYA",
    # k. Pemisah
    "----",
    # l. Kedatangan
    "TANGGAL TERAKHIR TIBA DI MESIR",
    # m. Pemisah
    "-----",
    # n. Tambahan
    "TANGGAL AWAL KEDATANGAN", "TAHUN ALATUL",
    "KESAN DI MESIR", "PESAN UNTUK MASISIR",
    # o. Unggahan (status saja)
    "FOTO PROFIL ID", "FOTO PASPOR HALAMAN DEPAN",
    "FOTO PASPOR HALAMAN AMANDEMEN", "SCAN KK/AKTA LAHIR",
]

def get_gsheet_client():
    try:
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    except Exception:
        try:
            creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
        except FileNotFoundError:
            return None
    return gspread.authorize(creds)

def append_to_sheet(data: dict):
    client = get_gsheet_client()
    if client is None:
        return False, "Credentials tidak ditemukan."
    try:
        sheet = client.open(SHEET_NAME).sheet1
        if not sheet.row_values(1):
            sheet.append_row(HEADERS)
        row = [data.get(h, "") for h in HEADERS]
        sheet.append_row(row)
        return True, "Data berhasil disimpan ✓"
    except Exception as e:
        return False, f"Gagal menyimpan: {str(e)}"


# ============================================================
# OCR — TESSERACT
# ============================================================
def parse_mrz(lines: list) -> dict:
    result = {}
    try:
        baris = []
        for l in lines:
            c = re.sub(r'[^A-Z0-9<]', '', l.upper().replace('¥','').replace('p<','P<'))
            if len(c) >= 30:
                baris.append(c)
        if len(baris) < 2:
            return result
        line1 = baris[0].ljust(44,'<')[:44]
        line2 = baris[1].ljust(44,'<')[:44]
        if '<<' in line1:
            np = line1[5:] if line1.startswith('P<') else line1
            np = re.sub(r'^[A-Z]{3}','', np)
            parts   = np.split('<<')
            surname = parts[0].replace('<',' ').strip()
            given   = parts[1].replace('<',' ').strip() if len(parts)>1 else ''
            result['nama'] = f"{given} {surname}".strip() if given else surname
        lc = re.sub(r'^[^A-Z0-9]','', line2)
        m  = re.match(r'([A-Z]{1,2}[0-9]{6,8})', lc)
        if m: result['nomor_paspor'] = m.group(1)
        dob = re.search(r'IDN[A-Z](\d{6})', line2)
        if dob:
            d=dob.group(1); yy=int(d[:2])
            result['tanggal_lahir'] = f"{d[4:6]}/{d[2:4]}/{1900+yy if yy>30 else 2000+yy}"
        exp = re.search(r'[MF](\d{6})', line2)
        if exp:
            e=exp.group(1)
            result['tgl_habis'] = f"{e[4:6]}/{e[2:4]}/{2000+int(e[:2])}"
    except Exception:
        pass
    return result

def extract_passport_data(text: str) -> dict:
    result = {}
    lines  = [l.strip() for l in text.split('\n') if l.strip()]
    full   = ' '.join(lines)

    # Nomor paspor
    fn = re.sub(r'\s+','', full)
    m  = re.search(r'([A-Z][0-9]{7,8})', fn)
    if m: result['nomor_paspor'] = m.group(1)

    # Nama
    skip = {'INDONESIA','PASSPORT','PASPOR','REPUBLIC','REPUBLIK',
            'NATIONALITY','KEWARGANEGARAAN','SURNAME','GIVEN','FULL',
            'NAME','NAMA','DATE','BIRTH','EXPIRY','PLACE','SEX','TYPE',
            'CODE','ISSUE','BANDUNG','JAKARTA','MALE','FEMALE','LAHIR',
            'BERLAKU','SURABAYA','MEDAN','MAKASSAR','SEMARANG','YOGYAKARTA',
            'CAIRO','MESIR','MAKKAH','MADINAH'}
    for line in lines:
        lc = re.sub(r'[^A-Za-z\s]','', line).strip()
        kk = lc.upper().split()
        if (len(kk)>=2 and lc==lc.upper() and
            all(len(k)>=2 for k in kk) and
            not any(k in skip for k in kk)):
            kb = [k for k in kk if len(k)>=3]
            if len(kb)>=2:
                result['nama'] = ' '.join(kb)
                break

    # Kantor penerbit — cari setelah berbagai label yang mungkin muncul di paspor Indonesia
    penerbit_patterns = [
        r'(?:Place of Issue|Tempat Pengeluaran|Issued at|PENERBIT)[:\s/]+([A-Z][A-Z\s]{3,25})',
        r'(?:ISSUED\s+(?:AT|BY|IN))[:\s]+([A-Z][A-Z\s]{3,25})',
        r'(?:TGL\.?\s*PENGELUARAN|DATE OF ISSUE)[^\n]*\n([A-Z][A-Z\s]{3,25})',
    ]
    for pat in penerbit_patterns:
        m = re.search(pat, full, re.IGNORECASE)
        if m:
            val = re.sub(r'\s+', ' ', m.group(1)).strip()
            if len(val) >= 3:
                result['kantor_penerbit'] = val[:35]
                break

    # Fallback kantor penerbit — cari baris setelah tanggal pengeluaran
    if not result.get('kantor_penerbit'):
        for i, line in enumerate(lines):
            if re.search(r'(?:PENGELUARAN|DATE OF ISSUE|ISSUED)', line, re.IGNORECASE):
                # Ambil baris berikutnya yang berisi teks kota/kantor
                for j in range(i+1, min(i+4, len(lines))):
                    candidate = re.sub(r'[^A-Za-z\s]', '', lines[j]).strip()
                    words = candidate.upper().split()
                    if (len(words) >= 1 and len(candidate) >= 3 and
                        candidate == candidate.upper() and
                        not any(w in {'DATE','EXPIRY','BIRTH','SEX','TYPE',
                                      'NATIONALITY','NAME','SURNAME'} for w in words)):
                        result['kantor_penerbit'] = candidate.strip()[:35]
                        break
                break

    # Kota lahir — cari setelah berbagai label
    lahir_patterns = [
        r'(?:Place of Birth|Tempat Lahir|LAHIR)[:\s/]+([A-Z][A-Z\s]{2,25})',
        r'(?:BORN\s+(?:AT|IN))[:\s]+([A-Z][A-Z\s]{2,25})',
        r'(?:KOTA\s+LAHIR)[:\s]+([A-Z][A-Z\s]{2,25})',
    ]
    for pat in lahir_patterns:
        m = re.search(pat, full, re.IGNORECASE)
        if m:
            val = re.sub(r'\s+', ' ', m.group(1)).strip()
            if len(val) >= 3:
                result['kota_lahir'] = val[:30]
                break

    # Fallback kota lahir — cari baris setelah "DATE OF BIRTH" / "TGL LAHIR"
    if not result.get('kota_lahir'):
        for i, line in enumerate(lines):
            if re.search(r'(?:DATE OF BIRTH|TGL\.?\s*LAHIR|TEMPAT.*LAHIR)', line, re.IGNORECASE):
                for j in range(i+1, min(i+4, len(lines))):
                    candidate = re.sub(r'[^A-Za-z\s]', '', lines[j]).strip()
                    words = candidate.upper().split()
                    if (len(words) >= 1 and len(candidate) >= 3 and
                        candidate == candidate.upper() and
                        not re.search(r'\d', lines[j]) and
                        not any(w in {'DATE','EXPIRY','ISSUE','SEX','TYPE',
                                      'NATIONALITY','NAME','MALE','FEMALE',
                                      'PASSPORT','PASPOR'} for w in words)):
                        result['kota_lahir'] = candidate.strip()[:30]
                        break
                break

    # Semua tanggal
    tanggal = re.findall(
        r'(\d{1,2}\s+(?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\s+\d{4})',
        full, re.IGNORECASE
    )
    if len(tanggal)>=1: result['tanggal_lahir']  = tanggal[0]
    if len(tanggal)>=2: result['tanggal_terbit'] = tanggal[1]
    if len(tanggal)>=3: result['tgl_habis']       = tanggal[2]
    elif len(tanggal)==2: result['tgl_habis']     = tanggal[-1]

    # MRZ backup
    mrz_lines = [l for l in lines if
                 len(re.sub(r'[^A-Z0-9<]','',l.upper()))>=25 and
                 ('<<' in l or re.search(r'[A-Z0-9<]{20,}',l))]
    if len(mrz_lines)>=2:
        md = parse_mrz(mrz_lines[-2:])
        for k in ['nama','nomor_paspor','tanggal_lahir','tgl_habis']:
            if not result.get(k) and md.get(k):
                result[k] = md[k]

    return result

def run_ocr(image: Image.Image) -> tuple:
    try:
        import pytesseract
    except ImportError:
        return {}, "pytesseract tidak terinstall."
    try:
        image = ImageOps.exif_transpose(image).convert("RGB")
        w,h   = image.size
        if w>1200 or h>1200:
            r = min(1200/w,1200/h)
            image = image.resize((int(w*r),int(h*r)), Image.LANCZOS)
        gray = image.convert("L")
        text = pytesseract.image_to_string(gray, config='--oem 3 --psm 6')
        data = extract_passport_data(text)
        return data, text
    except Exception as e:
        return {}, f"OCR error: {str(e)}"


# ============================================================
# VALIDASI
# ============================================================
def validasi_nama(nama: str) -> tuple:
    nama = nama.strip()
    if not nama: return False, "Nama tidak boleh kosong."
    kata = nama.split()
    if len(kata)==1:
        return False, "⚠️ Nama hanya 1 suku kata. Mohon lakukan amandemen penambahan nama pada paspor Anda terlebih dahulu."
    def is_inisial(k): return bool(re.match(r'^[A-Za-z]\.?$',k) or re.match(r'^[A-Za-z]{2}\.$',k))
    def is_muh(k): return k.rstrip('.').upper() in ('MUH','MUHAMAD','MUHAMMAD')
    if len(kata)==2:
        if is_inisial(kata[0]) and not is_muh(kata[0]):
            return False, "⚠️ Nama 2 suku kata dengan inisial di depan. Mohon lakukan amandemen penambahan nama pada paspor Anda terlebih dahulu."
        if is_inisial(kata[-1]) and not is_muh(kata[-1]):
            return False, "⚠️ Nama 2 suku kata dengan inisial di belakang. Mohon lakukan amandemen penambahan nama pada paspor Anda terlebih dahulu."
    return True, "✓ Valid"

def validasi_masa_berlaku(tgl: str) -> tuple:
    if not tgl: return False, "Tanggal habis berlaku tidak boleh kosong."
    m = re.search(r'\b(20\d{2}|19\d{2})\b', tgl)
    if not m: return False, "Format tanggal tidak dikenali."
    tahun = int(m.group(1))

    # Cek bulan jika tahun = 2027
    bulan_map = {'JAN':1,'FEB':2,'MAR':3,'APR':4,'MAY':5,'JUN':6,
                 'JUL':7,'AUG':8,'SEP':9,'OCT':10,'NOV':11,'DEC':12}
    bln_match = re.search(r'(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)', tgl.upper())
    tgl_match = re.search(r'\b(\d{1,2})\b', tgl)

    if tahun < 2027:
        return False, f"⚠️ Masa berlaku paspor berakhir tahun {tahun} (sebelum 31 Maret 2027). Mohon lakukan perpanjangan (renewal) paspor Anda terlebih dahulu."

    if tahun == 2027 and bln_match and tgl_match:
        bulan = bulan_map.get(bln_match.group(1), 0)
        tgl_n = int(tgl_match.group(1))
        if bulan < 3 or (bulan == 3 and tgl_n < 31):
            return False, "⚠️ Masa berlaku paspor habis sebelum 31 Maret 2027. Mohon lakukan perpanjangan (renewal) paspor Anda terlebih dahulu."

    return True, f"✓ Valid hingga {tgl}"


# ============================================================
# SESSION STATE
# ============================================================
def init_state():
    defaults = {
        'step': 1,
        'ocr_baru': {}, 'ocr_lama': {},
        'foto_profil': False, 'foto_paspor': False,
        'foto_amandemen': False, 'foto_kk': False,
        'submitted': False,
    }
    for k,v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# ============================================================
# HELPER — STEP INDICATOR
# ============================================================
def render_header():
    st.markdown("""
    <div class="intif-header">
        <div class="badge">🛂 INTIF Official</div>
        <h1>Form Pengisian ID INTIF</h1>
        <p>Immigration Tracking &amp; Information Facility &nbsp;|&nbsp; Formulir Digital Resmi</p>
    </div>
    """, unsafe_allow_html=True)

def render_steps(current):
    labels = ["📷 Dokumen", "📋 Paspor", "👤 Data Diri", "🏠 Alamat & Kontak", "✅ Kirim"]
    html   = '<div class="steps-wrap">'
    for i, label in enumerate(labels, 1):
        cls  = "done" if current>i else ("active" if current==i else "")
        icon = "✓"    if current>i else str(i)
        html += f'<div class="step-item {cls}"><div class="step-dot">{icon}</div>{label}</div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

def section(label):
    st.markdown(f'<div class="section-label">{label}</div>', unsafe_allow_html=True)

def nav_buttons(back_step=None, next_label="Lanjutkan →"):
    col1, col2 = st.columns(2)
    back = False
    nxt  = False
    with col1:
        if back_step and st.button("← Kembali", key=f"back_{back_step}"):
            back = True
    with col2:
        if st.button(next_label, key=f"next_{st.session_state.step}"):
            nxt = True
    return back, nxt


# ============================================================
# RENDER
# ============================================================
render_header()
render_steps(st.session_state.step)


# ════════════════════════════════════════════════════════════
# TAHAP 1 — UPLOAD DOKUMEN
# ════════════════════════════════════════════════════════════
if st.session_state.step == 1:
    st.markdown("""
    <div class="card">
        <div class="card-title">📷 Upload Dokumen</div>
        <div class="card-sub">Upload semua dokumen yang diperlukan. Foto paspor halaman depan wajib diupload untuk proses OCR otomatis.</div>
    </div>
    """, unsafe_allow_html=True)

    section("56 · FOTO PROFIL ID (Wajib)")
    st.caption("Pastikan wajah terlihat jelas, tidak memakai kacamata hitam, masker, atau cadar.")
    foto_profil = st.file_uploader("Upload Foto Profil", type=["jpg","jpeg","png","webp"], key="up_profil")
    if foto_profil:
        img = Image.open(foto_profil)
        col1,col2,col3 = st.columns([1,2,1])
        with col2: st.image(img, caption="Foto Profil", width=200)
        st.markdown('<div class="alert-warning">⚠️ Pastikan: wajah terlihat jelas, tidak ada kacamata hitam, masker, atau cadar. Foto akan ditolak jika wajah tidak terlihat jelas.</div>', unsafe_allow_html=True)
        profil_ok = st.checkbox("✅ Saya konfirmasi foto profil sudah sesuai ketentuan", key="chk_profil")
    else:
        profil_ok = False

    st.markdown("<hr>", unsafe_allow_html=True)
    section("57 · FOTO PASPOR HALAMAN DEPAN (Wajib — untuk OCR)")
    st.caption("Foto harus jelas dan mencakup seluruh halaman biodata termasuk 2 baris MRZ di bagian bawah.")
    foto_paspor = st.file_uploader("Upload Foto Paspor Halaman Depan", type=["jpg","jpeg","png","webp"], key="up_paspor")
    if foto_paspor:
        img2 = Image.open(foto_paspor)
        col1,col2,col3 = st.columns([1,2,1])
        with col2: st.image(img2, caption="Paspor Halaman Depan", width=280)
        paspor_ok = True
    else:
        paspor_ok = False

    st.markdown("<hr>", unsafe_allow_html=True)
    section("58 · FOTO PASPOR HALAMAN AMANDEMEN (Opsional)")
    foto_amandemen = st.file_uploader("Upload Halaman Amandemen (jika ada)", type=["jpg","jpeg","png","webp"], key="up_amandemen")
    if foto_amandemen:
        img3 = Image.open(foto_amandemen)
        col1,col2,col3 = st.columns([1,2,1])
        with col2: st.image(img3, caption="Halaman Amandemen", width=280)

    st.markdown("<hr>", unsafe_allow_html=True)
    section("59 · SCAN KARTU KELUARGA / AKTA LAHIR (Wajib)")
    foto_kk = st.file_uploader("Upload KK atau Akta Lahir", type=["jpg","jpeg","png","webp","pdf"], key="up_kk")
    if foto_kk:
        if foto_kk.type != "application/pdf":
            img4 = Image.open(foto_kk)
            col1,col2,col3 = st.columns([1,2,1])
            with col2: st.image(img4, caption="KK / Akta Lahir", width=280)
        else:
            st.success("✅ File PDF berhasil diupload")
        kk_ok = True
    else:
        kk_ok = False

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Proses OCR & Lanjutkan →", key="btn_step1"):
        errors = []
        if not foto_profil:  errors.append("Foto profil belum diupload.")
        elif not profil_ok:  errors.append("Harap konfirmasi foto profil sudah sesuai ketentuan.")
        if not foto_paspor:  errors.append("Foto paspor halaman depan belum diupload.")
        if not foto_kk:      errors.append("Scan KK / Akta Lahir belum diupload.")

        if errors:
            for e in errors:
                st.markdown(f'<div class="alert-danger">❌ {e}</div>', unsafe_allow_html=True)
        else:
            with st.spinner("Memproses OCR paspor... (5-15 detik)"):
                img_paspor = Image.open(foto_paspor)
                data_baru, _ = run_ocr(img_paspor)
                st.session_state.ocr_baru = data_baru

                # OCR paspor lama jika ada
                if foto_amandemen:
                    try:
                        img_lama = Image.open(foto_amandemen)
                        data_lama, _ = run_ocr(img_lama)
                        st.session_state.ocr_lama = data_lama
                    except Exception:
                        st.session_state.ocr_lama = {}

                st.session_state.foto_profil    = True
                st.session_state.foto_paspor    = True
                st.session_state.foto_amandemen = foto_amandemen is not None
                st.session_state.foto_kk        = True

                # Reset field form agar terisi ulang dari OCR
                fields_to_reset = [
                    'f_nama','f_nomor_paspor','f_kantor_penerbit',
                    'f_tgl_terbit','f_tgl_habis','f_kota_lahir','f_tgl_lahir',
                ]
                for f in fields_to_reset:
                    if f in st.session_state: del st.session_state[f]

                st.session_state.step = 2
                st.rerun()


# ════════════════════════════════════════════════════════════
# TAHAP 2 — DATA PASPOR
# ════════════════════════════════════════════════════════════
elif st.session_state.step == 2:
    ocr = st.session_state.ocr_baru
    ocr_lama = st.session_state.ocr_lama

    st.markdown("""
    <div class="card">
        <div class="card-title">📋 Verifikasi Data Paspor</div>
        <div class="card-sub">Periksa data hasil OCR. Koreksi jika ada yang salah atau kosong.</div>
    </div>
    """, unsafe_allow_html=True)

    # Inisialisasi default dari OCR
    field_defaults = {
        'f_nama':           ocr.get('nama',''),
        'f_nomor_paspor':   ocr.get('nomor_paspor',''),
        'f_kantor_penerbit':ocr.get('kantor_penerbit',''),
        'f_tgl_terbit':     ocr.get('tanggal_terbit',''),
        'f_tgl_habis':      ocr.get('tgl_habis',''),
        'f_kota_lahir':     ocr.get('kota_lahir',''),
        'f_tgl_lahir':      ocr.get('tanggal_lahir',''),
        'f_sijil':          '',
        'f_safhah':         '',
        'f_kekeluargaan':   '',
        'f_no_paspor_lama': ocr_lama.get('nomor_paspor',''),
        'f_penerbit_lama':  ocr_lama.get('kantor_penerbit',''),
        'f_terbit_lama':    ocr_lama.get('tanggal_terbit',''),
        'f_habis_lama':     ocr_lama.get('tgl_habis',''),
    }
    for k,v in field_defaults.items():
        if k not in st.session_state: st.session_state[k] = v

    section("a · DATA PASPOR BARU (hasil OCR — koreksi jika perlu)")
    nama          = st.text_input("1. NAMA LENGKAP",                key='f_nama')
    nomor_paspor  = st.text_input("2. NOMOR PASPOR",                key='f_nomor_paspor')
    kantor_penerbit=st.text_input("3. KANTOR PENERBIT PASPOR",      key='f_kantor_penerbit')
    tgl_terbit    = st.text_input("4. TANGGAL TERBIT PASPOR",       key='f_tgl_terbit')
    tgl_habis     = st.text_input("5. TANGGAL HABIS BERLAKU PASPOR",key='f_tgl_habis')
    kota_lahir    = st.text_input("6. KOTA KELAHIRAN",              key='f_kota_lahir')
    tgl_lahir     = st.text_input("7. TANGGAL LAHIR",               key='f_tgl_lahir')

    section("b · DATA TAMBAHAN PASPOR")
    sijil       = st.text_input("8. SIJIL",       key='f_sijil')
    safhah      = st.text_input("9. SAFHAH",      key='f_safhah')
    kekeluargaan= st.text_input("10. KEKELUARGAAN", key='f_kekeluargaan')

    section("c · DATA PASPOR LAMA (Opsional — hasil OCR halaman amandemen)")
    st.caption("Kosongkan jika tidak ada paspor lama.")
    no_paspor_lama = st.text_input("11. NO PASPOR LAMA",               key='f_no_paspor_lama')
    penerbit_lama  = st.text_input("12. KANTOR PENERBIT PASPOR LAMA",  key='f_penerbit_lama')
    terbit_lama    = st.text_input("13. TGL TERBIT PASPOR LAMA",       key='f_terbit_lama')
    habis_lama     = st.text_input("14. TGL HABIS PASPOR LAMA",        key='f_habis_lama')

    st.markdown("<br>", unsafe_allow_html=True)
    back, nxt = nav_buttons(back_step=1)

    if back:
        st.session_state.step = 1
        st.rerun()

    if nxt:
        # Validasi
        valid_nama, msg_nama = validasi_nama(nama)
        valid_habis, msg_habis = validasi_masa_berlaku(tgl_habis)
        errors = []
        if not valid_nama:             errors.append(msg_nama)
        if not valid_habis:            errors.append(msg_habis)
        if not nomor_paspor.strip():   errors.append("Nomor paspor tidak boleh kosong.")
        if not tgl_lahir.strip():      errors.append("Tanggal lahir tidak boleh kosong.")

        if errors:
            for e in errors:
                st.markdown(f'<div class="alert-danger">{e}</div>', unsafe_allow_html=True)
        else:
            # Simpan ke session
            st.session_state.update({
                'fd_nama': nama, 'fd_nomor_paspor': nomor_paspor,
                'fd_kantor_penerbit': kantor_penerbit, 'fd_tgl_terbit': tgl_terbit,
                'fd_tgl_habis': tgl_habis, 'fd_kota_lahir': kota_lahir,
                'fd_tgl_lahir': tgl_lahir, 'fd_sijil': sijil,
                'fd_safhah': safhah, 'fd_kekeluargaan': kekeluargaan,
                'fd_no_paspor_lama': no_paspor_lama, 'fd_penerbit_lama': penerbit_lama,
                'fd_terbit_lama': terbit_lama, 'fd_habis_lama': habis_lama,
            })
            st.session_state.step = 3
            st.rerun()


# ════════════════════════════════════════════════════════════
# TAHAP 3 — DATA DIRI & PENDIDIKAN
# ════════════════════════════════════════════════════════════
elif st.session_state.step == 3:
    st.markdown("""
    <div class="card">
        <div class="card-title">👤 Data Diri & Pendidikan</div>
        <div class="card-sub">Lengkapi data diri dan informasi pendidikan Anda.</div>
    </div>
    """, unsafe_allow_html=True)

    diri_defaults = {
        'f_jk':'', 'f_id_kk':'', 'f_status_kk':'', 'f_thn_datang':'',
        'f_nama_sma':'', 'f_nama_arab':'', 'f_tentang':'', 'f_catatan':'',
        'f_lembaga':'', 'f_fakultas':'', 'f_jurusan':'', 'f_tingkat':'', 'f_thn_ajaran':'',
    }
    for k,v in diri_defaults.items():
        if k not in st.session_state: st.session_state[k] = v

    section("d · DATA DIRI")
    jk = st.selectbox("15. JENIS KELAMIN", ["","Laki-laki","Perempuan"], key='f_jk')
    id_kk      = st.text_input("16. ID KK",                        key='f_id_kk')
    status_kk  = st.text_input("17. STATUS KK",                    key='f_status_kk')
    thn_datang = st.text_input("18. TAHUN KEDATANGAN",             key='f_thn_datang')
    nama_sma   = st.text_input("19. NAMA SMA/PONDOK/SEDERAJAT",   key='f_nama_sma')
    nama_arab  = st.text_input("20. NAMA ARAB",                    key='f_nama_arab')
    tentang    = st.text_area("21. TENTANG ANDA",                  key='f_tentang', height=100)
    catatan    = st.text_area("22. CATATAN KHUSUS",                key='f_catatan',  height=80)

    section("f · KETERANGAN PENDIDIKAN")
    lembaga    = st.text_input("24. LEMBAGA PENDIDIKAN",           key='f_lembaga')
    fakultas   = st.text_input("25. FAKULTAS",                     key='f_fakultas')
    jurusan    = st.text_input("26. JURUSAN",                      key='f_jurusan')
    tingkat    = st.text_input("27. TINGKAT/KELAS",                key='f_tingkat')
    thn_ajaran = st.text_input("28. TAHUN AJARAN",                 key='f_thn_ajaran')

    st.markdown("<br>", unsafe_allow_html=True)
    back, nxt = nav_buttons(back_step=2)

    if back:
        st.session_state.step = 2
        st.rerun()

    if nxt:
        errors = []
        if not jk: errors.append("Jenis kelamin harus dipilih.")
        if errors:
            for e in errors:
                st.markdown(f'<div class="alert-danger">{e}</div>', unsafe_allow_html=True)
        else:
            st.session_state.update({
                'fd_jk': jk, 'fd_id_kk': id_kk, 'fd_status_kk': status_kk,
                'fd_thn_datang': thn_datang, 'fd_nama_sma': nama_sma,
                'fd_nama_arab': nama_arab, 'fd_tentang': tentang,
                'fd_catatan': catatan, 'fd_lembaga': lembaga,
                'fd_fakultas': fakultas, 'fd_jurusan': jurusan,
                'fd_tingkat': tingkat, 'fd_thn_ajaran': thn_ajaran,
            })
            st.session_state.step = 4
            st.rerun()


# ════════════════════════════════════════════════════════════
# TAHAP 4 — ALAMAT, KONTAK & TAMBAHAN
# ════════════════════════════════════════════════════════════
elif st.session_state.step == 4:
    st.markdown("""
    <div class="card">
        <div class="card-title">🏠 Alamat, Kontak & Data Tambahan</div>
        <div class="card-sub">Lengkapi alamat tinggal, kontak, dan informasi tambahan lainnya.</div>
    </div>
    """, unsafe_allow_html=True)

    kontak_defaults = {
        'f_area':'','f_imarah':'','f_lantai':'','f_syaqqah':'',
        'f_jalan':'','f_distrik':'','f_kawasan':'','f_provinsi':'',
        'f_telp':'','f_wa':'','f_email':'','f_surel':'',
        'f_fb':'','f_ig':'','f_tw':'',
        'f_telp_teman':'','f_telp_darurat':'','f_telp_darurat2':'',
        'f_tgl_tiba':'','f_tgl_awal':'','f_thn_alatul':'',
        'f_kesan':'','f_pesan':'',
    }
    for k,v in kontak_defaults.items():
        if k not in st.session_state: st.session_state[k] = v

    section("h · KETERANGAN ALAMAT")
    col1,col2 = st.columns(2)
    with col1:
        area    = st.text_input("30. AREA",         key='f_area')
        lantai  = st.text_input("32. LANTAI",       key='f_lantai')
        jalan   = st.text_input("34. NAMA JALAN",   key='f_jalan')
        kawasan = st.text_input("36. KAWASAN",      key='f_kawasan')
    with col2:
        imarah  = st.text_input("31. NO. IMARAH",   key='f_imarah')
        syaqqah = st.text_input("33. NO. SYAQQAH",  key='f_syaqqah')
        distrik = st.text_input("35. DISTRIK",      key='f_distrik')
        provinsi= st.text_input("37. PROVINSI",     key='f_provinsi')

    section("j · KONTAK")
    col1,col2 = st.columns(2)
    with col1:
        telp   = st.text_input("39. NOMOR TELEPON",    key='f_telp')
        email  = st.text_input("41. EMAIL ADDRESS",    key='f_email')
        fb     = st.text_input("43. FACEBOOK",         key='f_fb')
        tw     = st.text_input("45. TWITTER",          key='f_tw')
    with col2:
        wa     = st.text_input("40. NOMOR WHATSAPP",   key='f_wa')
        surel  = st.text_input("42. SUREL",            key='f_surel')
        ig     = st.text_input("44. INSTAGRAM",        key='f_ig')

    telp_teman    = st.text_input("46. NOMOR TELEPON TEMAN RUMAH",      key='f_telp_teman')
    telp_darurat  = st.text_input("47. NOMOR TELEPON DARURAT",          key='f_telp_darurat')
    telp_darurat2 = st.text_input("48. NOMOR TELEPON DARURAT LAINNYA",  key='f_telp_darurat2')

    section("l · TANGGAL KEDATANGAN")
    tgl_tiba = st.text_input("50. TANGGAL TERAKHIR TIBA DI MESIR (DD/MM/YYYY)", key='f_tgl_tiba')

    section("n · DATA TAMBAHAN")
    tgl_awal   = st.text_input("52. TANGGAL AWAL KEDATANGAN (DD/MM/YYYY)", key='f_tgl_awal')
    thn_alatul = st.text_input("53. TAHUN ALATUL",                          key='f_thn_alatul')
    kesan      = st.text_area("54. KESAN DI MESIR",  key='f_kesan', height=100)
    pesan      = st.text_area("55. PESAN UNTUK MASISIR", key='f_pesan', height=100)

    st.markdown("<br>", unsafe_allow_html=True)
    back, nxt = nav_buttons(back_step=3, next_label="Review & Kirim →")

    if back:
        st.session_state.step = 3
        st.rerun()

    if nxt:
        errors = []
        if not telp.strip() and not wa.strip():
            errors.append("Minimal satu nomor telepon (Telepon atau WhatsApp) harus diisi.")
        if errors:
            for e in errors:
                st.markdown(f'<div class="alert-danger">{e}</div>', unsafe_allow_html=True)
        else:
            st.session_state.update({
                'fd_area': area, 'fd_imarah': imarah, 'fd_lantai': lantai,
                'fd_syaqqah': syaqqah, 'fd_jalan': jalan, 'fd_distrik': distrik,
                'fd_kawasan': kawasan, 'fd_provinsi': provinsi,
                'fd_telp': telp, 'fd_wa': wa, 'fd_email': email, 'fd_surel': surel,
                'fd_fb': fb, 'fd_ig': ig, 'fd_tw': tw,
                'fd_telp_teman': telp_teman, 'fd_telp_darurat': telp_darurat,
                'fd_telp_darurat2': telp_darurat2, 'fd_tgl_tiba': tgl_tiba,
                'fd_tgl_awal': tgl_awal, 'fd_thn_alatul': thn_alatul,
                'fd_kesan': kesan, 'fd_pesan': pesan,
            })
            st.session_state.step = 5
            st.rerun()


# ════════════════════════════════════════════════════════════
# TAHAP 5 — REVIEW & KIRIM
# ════════════════════════════════════════════════════════════
elif st.session_state.step == 5:
    if not st.session_state.submitted:
        g = st.session_state.get  # shorthand

        st.markdown("""
        <div class="card fade-in">
            <div class="card-title">✅ Review & Konfirmasi</div>
            <div class="card-sub">Periksa semua data sebelum mengirim. Tekan "Edit" untuk kembali ke tahap sebelumnya.</div>
        </div>
        """, unsafe_allow_html=True)

        def trow(label, val):
            return f"<tr><td>{label}</td><td>{val or '—'}</td></tr>"

        def thead(label):
            return f"<tr><td colspan='2' class='confirm-section'>{label}</td></tr>"

        html = '<div class="card" style="padding:0"><table class="confirm-table">'
        html += thead("DATA PASPOR BARU")
        html += trow("1. Nama Lengkap",              g('fd_nama',''))
        html += trow("2. Nomor Paspor",              g('fd_nomor_paspor',''))
        html += trow("3. Kantor Penerbit",           g('fd_kantor_penerbit',''))
        html += trow("4. Tgl Terbit",                g('fd_tgl_terbit',''))
        html += trow("5. Tgl Habis Berlaku",         g('fd_tgl_habis',''))
        html += trow("6. Kota Kelahiran",            g('fd_kota_lahir',''))
        html += trow("7. Tanggal Lahir",             g('fd_tgl_lahir',''))
        html += thead("DATA TAMBAHAN PASPOR")
        html += trow("8. Sijil",                     g('fd_sijil',''))
        html += trow("9. Safhah",                    g('fd_safhah',''))
        html += trow("10. Kekeluargaan",             g('fd_kekeluargaan',''))
        html += thead("DATA PASPOR LAMA")
        html += trow("11. No Paspor Lama",           g('fd_no_paspor_lama',''))
        html += trow("12. Penerbit Lama",            g('fd_penerbit_lama',''))
        html += trow("13. Tgl Terbit Lama",          g('fd_terbit_lama',''))
        html += trow("14. Tgl Habis Lama",           g('fd_habis_lama',''))
        html += thead("DATA DIRI")
        html += trow("15. Jenis Kelamin",            g('fd_jk',''))
        html += trow("16. ID KK",                   g('fd_id_kk',''))
        html += trow("17. Status KK",               g('fd_status_kk',''))
        html += trow("18. Tahun Kedatangan",         g('fd_thn_datang',''))
        html += trow("19. Nama SMA/Pondok",          g('fd_nama_sma',''))
        html += trow("20. Nama Arab",               g('fd_nama_arab',''))
        html += thead("PENDIDIKAN")
        html += trow("24. Lembaga Pendidikan",       g('fd_lembaga',''))
        html += trow("25. Fakultas",                g('fd_fakultas',''))
        html += trow("26. Jurusan",                 g('fd_jurusan',''))
        html += trow("27. Tingkat/Kelas",           g('fd_tingkat',''))
        html += trow("28. Tahun Ajaran",            g('fd_thn_ajaran',''))
        html += thead("ALAMAT")
        html += trow("30. Area",                    g('fd_area',''))
        html += trow("31. No. Imarah",              g('fd_imarah',''))
        html += trow("32. Lantai",                  g('fd_lantai',''))
        html += trow("33. No. Syaqqah",             g('fd_syaqqah',''))
        html += trow("34. Nama Jalan",              g('fd_jalan',''))
        html += trow("35. Distrik",                 g('fd_distrik',''))
        html += trow("36. Kawasan",                 g('fd_kawasan',''))
        html += trow("37. Provinsi",                g('fd_provinsi',''))
        html += thead("KONTAK")
        html += trow("39. Nomor Telepon",           g('fd_telp',''))
        html += trow("40. WhatsApp",                g('fd_wa',''))
        html += trow("41. Email",                   g('fd_email',''))
        html += trow("47. Telp Darurat",            g('fd_telp_darurat',''))
        html += thead("KEDATANGAN & TAMBAHAN")
        html += trow("50. Tgl Tiba di Mesir",       g('fd_tgl_tiba',''))
        html += trow("52. Tgl Awal Kedatangan",     g('fd_tgl_awal',''))
        html += trow("53. Tahun Alatul",            g('fd_thn_alatul',''))
        html += thead("UNGGAHAN")
        html += trow("56. Foto Profil",             "✅ Terupload" if g('foto_profil') else "—")
        html += trow("57. Foto Paspor Depan",       "✅ Terupload" if g('foto_paspor') else "—")
        html += trow("58. Halaman Amandemen",       "✅ Terupload" if g('foto_amandemen') else "Tidak ada")
        html += trow("59. KK / Akta Lahir",         "✅ Terupload" if g('foto_kk') else "—")
        html += '</table></div>'
        st.markdown(html, unsafe_allow_html=True)

        col1,col2,col3 = st.columns(3)
        with col1:
            if st.button("← Edit Paspor", key="edit2"):
                st.session_state.step = 2; st.rerun()
        with col2:
            if st.button("← Edit Data Diri", key="edit3"):
                st.session_state.step = 3; st.rerun()
        with col3:
            if st.button("← Edit Alamat", key="edit4"):
                st.session_state.step = 4; st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("📤 KIRIM PERMOHONAN SEKARANG", key="btn_submit"):
            with st.spinner("Mengirim data ke sistem INTIF..."):
                g = st.session_state.get
                data = {
                    "NAMA LENGKAP":                g('fd_nama',''),
                    "NOMOR PASPOR":                g('fd_nomor_paspor',''),
                    "KANTOR PENERBIT PASPOR":      g('fd_kantor_penerbit',''),
                    "TANGGAL TERBIT PASPOR":       g('fd_tgl_terbit',''),
                    "TANGGAL HABIS BERLAKU PASPOR":g('fd_tgl_habis',''),
                    "KOTA KELAHIRAN":              g('fd_kota_lahir',''),
                    "TANGGAL LAHIR":               g('fd_tgl_lahir',''),
                    "SIJIL":                       g('fd_sijil',''),
                    "SAFHAH":                      g('fd_safhah',''),
                    "KEKELUARGAAN":                g('fd_kekeluargaan',''),
                    "NO PASPOR LAMA":              g('fd_no_paspor_lama',''),
                    "KANTOR PENERBIT PASPOR LAMA": g('fd_penerbit_lama',''),
                    "TGL TERBIT PASPOR LAMA":      g('fd_terbit_lama',''),
                    "TGL HABIS PASPOR LAMA":       g('fd_habis_lama',''),
                    "JENIS KELAMIN":               g('fd_jk',''),
                    "ID KK":                       g('fd_id_kk',''),
                    "STATUS KK":                   g('fd_status_kk',''),
                    "TAHUN KEDATANGAN":            g('fd_thn_datang',''),
                    "NAMA SMA/PONDOK/SEDERAJAT":   g('fd_nama_sma',''),
                    "NAMA ARAB":                   g('fd_nama_arab',''),
                    "TENTANG ANDA":                g('fd_tentang',''),
                    "CATATAN KHUSUS":              g('fd_catatan',''),
                    "-":                           "-",
                    "LEMBAGA PENDIDIKAN":          g('fd_lembaga',''),
                    "FAKULTAS":                    g('fd_fakultas',''),
                    "JURUSAN":                     g('fd_jurusan',''),
                    "TINGKAT/KELAS":               g('fd_tingkat',''),
                    "TAHUN AJARAN":                g('fd_thn_ajaran',''),
                    "--":                          "--",
                    "AREA":                        g('fd_area',''),
                    "NO. IMARAH":                  g('fd_imarah',''),
                    "LANTAI":                      g('fd_lantai',''),
                    "NO. SYAQQAH":                 g('fd_syaqqah',''),
                    "NAMA JALAN":                  g('fd_jalan',''),
                    "DISTRIK":                     g('fd_distrik',''),
                    "KAWASAN":                     g('fd_kawasan',''),
                    "PROVINSI":                    g('fd_provinsi',''),
                    "---":                         "---",
                    "NOMOR TELEPON":               g('fd_telp',''),
                    "NOMOR WHATSAPP":              g('fd_wa',''),
                    "EMAIL ADDRESS":               g('fd_email',''),
                    "SUREL":                       g('fd_surel',''),
                    "FACEBOOK":                    g('fd_fb',''),
                    "INSTAGRAM":                   g('fd_ig',''),
                    "TWITTER":                     g('fd_tw',''),
                    "NOMOR TELEPON TEMAN RUMAH":   g('fd_telp_teman',''),
                    "NOMOR TELEPON DARURAT":       g('fd_telp_darurat',''),
                    "NOMOR TELEPON DARURAT LAINNYA":g('fd_telp_darurat2',''),
                    "----":                        "----",
                    "TANGGAL TERAKHIR TIBA DI MESIR": g('fd_tgl_tiba',''),
                    "-----":                       "-----",
                    "TANGGAL AWAL KEDATANGAN":     g('fd_tgl_awal',''),
                    "TAHUN ALATUL":                g('fd_thn_alatul',''),
                    "KESAN DI MESIR":              g('fd_kesan',''),
                    "PESAN UNTUK MASISIR":         g('fd_pesan',''),
                    "FOTO PROFIL ID":              "Terupload" if g('foto_profil') else "",
                    "FOTO PASPOR HALAMAN DEPAN":   "Terupload" if g('foto_paspor') else "",
                    "FOTO PASPOR HALAMAN AMANDEMEN":"Terupload" if g('foto_amandemen') else "",
                    "SCAN KK/AKTA LAHIR":          "Terupload" if g('foto_kk') else "",
                }
                ok, msg = append_to_sheet(data)
                if ok:
                    st.session_state.submitted = True
                    st.rerun()
                else:
                    st.error(f"❌ {msg}")

    else:
        # Sukses
        st.markdown("""
        <div class="card fade-in" style="text-align:center;padding:48px 28px;">
            <div style="font-size:3.5rem;margin-bottom:16px;">🎉</div>
            <div style="font-family:'Playfair Display',serif;font-size:1.5rem;
                        color:#0B1F3A;font-weight:700;margin-bottom:12px;">
                Permohonan Berhasil Dikirim!
            </div>
            <div style="font-size:0.88rem;color:#6b7588;line-height:1.8;margin-bottom:28px;">
                Data Anda telah tercatat dalam sistem INTIF.<br>
                Tim kami akan menghubungi Anda dalam waktu 1x24 jam kerja.
            </div>
            <div class="alert-success">✓ Data tersimpan otomatis ke Google Sheets INTIF</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🔄 Isi Form Baru", key="btn_reset"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.session_state.step = 1
            st.rerun()


# ============================================================
# FOOTER
# ============================================================
st.markdown("""
<div class="footer">
    © 2025 INTIF — Immigration Tracking & Information Facility<br>
    Sistem Digital Resmi Perpanjangan Izin Tinggal &nbsp;|&nbsp; Kerahasiaan data terjamin
</div>
""", unsafe_allow_html=True)
