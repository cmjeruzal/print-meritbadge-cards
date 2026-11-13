import pymupdf
import pandas as pd

# =====================================================
# Configuration
# =====================================================

CSV_FILE = "Merit_Badges_by_Scout.csv"
TEMPLATE_PDF = "merit_badge_pocket_cert_template.pdf"
OUTPUT_PDF = "Merit_Badge_Certificates.pdf"

SIGNATURE_FILE = "signature.png"

RECORDS_PER_PAGE = 8

UNIT = "Your Unit #"
COUNCIL = "Your Council Name"

# Printer calibration
X_OFFSET = 0
Y_OFFSET = 3

# Signature sizing adjustments
SIGNATURE_X_PADDING = 60
SIGNATURE_Y_PADDING = 20

# Font sizes
NAME_FONT_SIZE = 10
BADGE_FONT_SIZE = 10
DATE_FONT_SIZE = 10
UNIT_FONT_SIZE = 10
COUNCIL_FONT_SIZE = 10

# =====================================================
# Extract field coordinates from template
# =====================================================

template_doc = pymupdf.open(TEMPLATE_PDF)
template_page = template_doc[0]

field_positions = {}

for widget in template_page.widgets():
    field_positions[widget.field_name] = widget.rect

page_width = template_page.rect.width
page_height = template_page.rect.height

template_doc.close()

print(f"Loaded {len(field_positions)} field positions")

# =====================================================
# Read spreadsheet
# =====================================================

df = pd.read_csv(CSV_FILE, encoding="utf-8")

# Preserve spreadsheet order exactly
# No sorting

# =====================================================
# Helper Function
# =====================================================

def insert_fitted_centered_text(
    page,
    rect,
    text,
    max_font_size=10,
    min_font_size=6
):
    """
    Center text in a field and reduce the
    font size until it fits.
    """

    for font_size in range(max_font_size, min_font_size - 1, -1):

        rc = page.insert_textbox(
            rect,
            str(text),
            fontsize=font_size,
            fontname="helv",
            align=1,  # centered
        )

        if rc >= 0:
            return

    # Nothing fit (usually the field is too short for the line height).
    # insert_textbox writes nothing on failure, so grow the rect downward
    # by the shortfall and insert at the minimum size rather than skipping.
    rect = pymupdf.Rect(rect.x0, rect.y0, rect.x1, rect.y1 - rc + 1)
    page.insert_textbox(
        rect,
        str(text),
        fontsize=min_font_size,
        fontname="helv",
        align=1,
    )

# =====================================================
# Create Output PDF
# =====================================================

output_doc = pymupdf.open()

for start in range(0, len(df), RECORDS_PER_PAGE):

    page = output_doc.new_page(
        width=page_width,
        height=page_height
    )

    batch = df.iloc[start:start + RECORDS_PER_PAGE]

    for slot, (_, row) in enumerate(batch.iterrows(), start=1):

        earned_date = pd.to_datetime(row["Date Earned"])

        date_text = (
            f"{earned_date.month}/"
            f"{earned_date.day}/"
            f"{earned_date.year}"
        )

        values = {
            f"Name {slot}": str(row["Scout Name"]),
            f"Badge {slot}": str(row["Merit Badge"]),
            f"Date {slot}": date_text,
            f"Unit {slot}": UNIT,
            f"Council {slot}": COUNCIL,
        }

        # ------------------------------------------
        # Text Fields
        # ------------------------------------------

        for field_name, value in values.items():

            if field_name not in field_positions:
                continue

            rect = field_positions[field_name]

            rect = pymupdf.Rect(
                rect.x0 + X_OFFSET,
                rect.y0 + Y_OFFSET,
                rect.x1 + X_OFFSET,
                rect.y1 + Y_OFFSET,
            )

            if field_name.startswith("Badge"):
                max_font_size = BADGE_FONT_SIZE
                min_font_size = 6

            elif field_name.startswith("Name"):
                max_font_size = NAME_FONT_SIZE
                min_font_size = 7

            elif field_name.startswith("Council"):
                max_font_size = COUNCIL_FONT_SIZE
                min_font_size = 7

            elif field_name.startswith("Unit"):
                max_font_size = UNIT_FONT_SIZE
                min_font_size = 8

            elif field_name.startswith("Date"):
                max_font_size = DATE_FONT_SIZE
                min_font_size = 8

            else:
                max_font_size = 10
                min_font_size = 6

            insert_fitted_centered_text(
                page,
                rect,
                value,
                max_font_size=max_font_size,
                min_font_size=min_font_size
            )

        # ------------------------------------------
        # Signature Image
        # ------------------------------------------

        signature_field = f"Unit Leader {slot}"

        if signature_field in field_positions:

            sig_rect = field_positions[signature_field]

            sig_rect = pymupdf.Rect(
                sig_rect.x0 + X_OFFSET - SIGNATURE_X_PADDING,
                sig_rect.y0 + Y_OFFSET - SIGNATURE_Y_PADDING,
                sig_rect.x1 + X_OFFSET + SIGNATURE_X_PADDING,
                sig_rect.y1 + Y_OFFSET + SIGNATURE_Y_PADDING,
            )

            page.insert_image(
                sig_rect,
                filename=SIGNATURE_FILE,
                keep_proportion=True,
            )

# =====================================================
# Save Output
# =====================================================

output_doc.save(
    OUTPUT_PDF,
    garbage=4,
    deflate=True
)

output_doc.close()

print()
print("=" * 50)
print(f"Certificates : {len(df)}")
print(f"Pages        : {(len(df) + 7) // 8}")
print(f"Output       : {OUTPUT_PDF}")
print("=" * 50)