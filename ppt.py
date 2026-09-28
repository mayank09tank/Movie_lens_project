from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

prs = Presentation()
prs.slide_width = Inches(13.33)
prs.slide_height = Inches(7.5)

BG = RGBColor(0x1e, 0x1e, 0x2e)
ACCENT = RGBColor(0x89, 0xb4, 0xfa)
WHITE = RGBColor(0xff, 0xff, 0xff)
GREEN = RGBColor(0xa6, 0xe3, 0xa1)
RED = RGBColor(0xf3, 0x8b, 0xa8)
YELLOW = RGBColor(0xf9, 0xe2, 0xaf)
GRAY = RGBColor(0x31, 0x32, 0x44)


def set_bg(slide):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = BG


def add_textbox(slide, text, left, top, width, height,
                size=18, bold=False, color=WHITE, align=PP_ALIGN.LEFT, wrap=True):
    txBox = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    txBox.word_wrap = wrap
    tf = txBox.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    return txBox


def add_code_box(slide, code, left, top, width, height):
    box = slide.shapes.add_shape(1, Inches(left), Inches(top), Inches(width), Inches(height))
    box.fill.solid()
    box.fill.fore_color.rgb = GRAY
    box.line.color.rgb = ACCENT
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = code
    run.font.size = Pt(13)
    run.font.color.rgb = GREEN
    run.font.name = "Courier New"


# ── Slide 1: Title ─────────────────────────────────────────────────────────────
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_bg(slide)
add_textbox(slide, "Errors / Issues Faced", 1, 2.5, 11, 1.2, size=40, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)
add_textbox(slide, "PostgreSQL Project — MovieLens", 1, 3.8, 11, 0.6, size=22, color=WHITE, align=PP_ALIGN.CENTER)


# ── Slide 2: Error 1 ───────────────────────────────────────────────────────────
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_bg(slide)
add_textbox(slide, "Issue 1: missing FROM-clause entry for table \"tag\"", 0.4, 0.2, 12.5, 0.6, size=24, bold=True, color=RED)
add_textbox(slide, "Error:", 0.4, 1.0, 2, 0.4, size=16, bold=True, color=YELLOW)
add_code_box(slide, 'ERROR: missing FROM-clause entry for table "tag"\nLINE 83: h.timestamp = tag.timestamp', 0.4, 1.45, 12.2, 0.9)
add_textbox(slide, "Reason:", 0.4, 2.5, 2, 0.4, size=16, bold=True, color=YELLOW)
add_textbox(slide, "Query mein tag.timestamp likha tha, lekin tag naam ka koi table/alias defined nahi tha.", 0.4, 2.95, 12.2, 0.6, size=16, color=WHITE)
add_textbox(slide, "Wrong:", 0.4, 3.65, 2, 0.4, size=16, bold=True, color=RED)
add_code_box(slide, "h.timestamp = tag.timestamp", 0.4, 4.1, 5.5, 0.6)
add_textbox(slide, "Correct:", 7.0, 3.65, 2, 0.4, size=16, bold=True, color=GREEN)
add_code_box(slide, "h.timestamp = tags.tag_timestamp", 7.0, 4.1, 5.5, 0.6)
add_textbox(slide, "Learning: Table name aur column name ko correctly reference karna zaroori hai.", 0.4, 5.0, 12.2, 0.6, size=15, color=ACCENT)


# ── Slide 3: Error 2 ───────────────────────────────────────────────────────────
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_bg(slide)
add_textbox(slide, "Issue 2: movies_history mein expected history record nahi bana", 0.4, 0.2, 12.5, 0.6, size=24, bold=True, color=RED)
add_textbox(slide, "Issue — Expected:", 0.4, 1.0, 4, 0.4, size=16, bold=True, color=YELLOW)
add_code_box(slide, "Toy Story (1995)            | FALSE | INSERT\nToy Story (1995) - VERSION 2 | TRUE  | UPDATE", 0.4, 1.45, 12.2, 0.9)
add_textbox(slide, "Actual mein sirf:", 0.4, 2.5, 4, 0.4, size=16, bold=True, color=YELLOW)
add_code_box(slide, "Toy Story - UPDATED... | TRUE | INSERT", 0.4, 2.95, 12.2, 0.6)
add_textbox(slide, "Reason:", 0.4, 3.7, 2, 0.4, size=16, bold=True, color=YELLOW)
add_textbox(slide,
    "movies table mein data pehle hi update ho chuka tha. Jab history table populate ki gayi,\n"
    "tab current updated data hi history mein insert hua.",
    0.4, 4.15, 12.2, 0.8, size=15, color=WHITE)
add_textbox(slide,
    "Learning: History/SCD Type 2 ko maintain karne ke liye update ke time old aur new versions capture karne padte hain.",
    0.4, 5.2, 12.2, 0.6, size=15, color=ACCENT)


# ── Slide 4: Error 3 ───────────────────────────────────────────────────────────
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_bg(slide)
add_textbox(slide, "Issue 3: movies UPDATE ke baad movies_history automatically update nahi hui", 0.4, 0.2, 12.5, 0.6, size=24, bold=True, color=RED)
add_textbox(slide, "Issue:", 0.4, 1.0, 2, 0.4, size=16, bold=True, color=YELLOW)
add_code_box(slide, "movies\n  ↓\nUPDATE\n  ↓\nmovies_history\n\nautomatic history record nahi bana.", 0.4, 1.45, 5, 1.8)
add_textbox(slide, "Reason:", 6.0, 1.0, 2, 0.4, size=16, bold=True, color=YELLOW)
add_textbox(slide, "movies table par koi trigger configured nahi tha.", 6.0, 1.45, 6.8, 0.5, size=15, color=WHITE)
add_textbox(slide, "Query to check triggers:", 6.0, 2.1, 6.8, 0.4, size=15, bold=True, color=YELLOW)
add_code_box(slide,
    "SELECT trigger_name, event_manipulation, action_statement\n"
    "FROM information_schema.triggers\n"
    "WHERE event_object_table = 'movies';",
    6.0, 2.55, 6.8, 1.1)
add_code_box(slide, "Result: 0 rows", 6.0, 3.75, 6.8, 0.5)
add_textbox(slide,
    "Solution: movies table par an appropriate UPDATE trigger create karna hoga\n"
    "jo movies_history mein old/new versions maintain kare.",
    0.4, 5.0, 12.2, 0.8, size=15, color=ACCENT)


# ── Slide 5: Error 4 ───────────────────────────────────────────────────────────
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_bg(slide)
add_textbox(slide, "Issue 4: CDC table create karne ke baad automatic CDC expect karna", 0.4, 0.2, 12.5, 0.6, size=24, bold=True, color=RED)
add_textbox(slide, "Issue:", 0.4, 1.0, 2, 0.4, size=16, bold=True, color=YELLOW)
add_textbox(slide, "movies_cdc table create karne ke baad initially koi CDC record nahi aaya.", 0.4, 1.45, 12.2, 0.5, size=15, color=WHITE)
add_textbox(slide, "Reason:", 0.4, 2.1, 2, 0.4, size=16, bold=True, color=YELLOW)
add_code_box(slide, "CREATE TABLE movies_cdc (...)", 0.4, 2.55, 6, 0.6)
add_textbox(slide, "sirf CDC table create karta hai. Isse automatically changes capture nahi hote.", 0.4, 3.25, 12.2, 0.5, size=15, color=WHITE)
add_textbox(slide, "Actual flow ke liye:", 0.4, 3.85, 4, 0.4, size=15, bold=True, color=YELLOW)
add_code_box(slide, "movies\n  ↓\nUPDATE\n  ↓\nTRIGGER\n  ↓\nmovies_cdc", 0.4, 4.3, 4, 1.8)
add_textbox(slide, "required hai.", 4.6, 4.3, 3, 0.4, size=15, color=WHITE)
add_textbox(slide, "Learning: CDC table aur CDC mechanism alag cheezein hain.", 0.4, 6.5, 12.2, 0.5, size=15, color=ACCENT)


prs.save(r"d:\OneDrive\Desktop\Postgres\Errors_Issues_Faced.pptx")
print("PPT saved: Errors_Issues_Faced.pptx")
