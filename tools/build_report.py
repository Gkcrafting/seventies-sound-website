from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from PIL import Image, ImageDraw, ImageFont

root = Path(__file__).resolve().parents[1] / "planning-and-research"
research = root / "research-notes"
report_folder = root.parent / "report"
report_folder.mkdir(exist_ok=True)
doc = Document()
section = doc.sections[0]
section.page_width = Inches(8.27)
section.page_height = Inches(11.69)
section.top_margin = section.bottom_margin = Inches(0.65)
section.left_margin = section.right_margin = Inches(0.75)
style = doc.styles["Normal"]
style.font.name = "Calibri"
style.font.size = Pt(11)
style.paragraph_format.space_after = Pt(7)
style.paragraph_format.line_spacing = 1.05
for name, size in [("Title", 23), ("Heading 1", 17), ("Heading 2", 13)]:
    doc.styles[name].font.name = "Calibri"
    doc.styles[name].font.size = Pt(size)
footer = section.footer.paragraphs[0]
footer.alignment = 2
field = OxmlElement("w:fldSimple")
field.set(qn("w:instr"), "PAGE")
footer._p.append(field)


def p(text):
    return doc.add_paragraph(text)


def heading(text):
    doc.add_heading(text, 2)


def page(title):
    doc.add_heading(title, 2)


def photo(name, caption):
    doc.add_picture(str(research / name), width=Inches(3.7))
    doc.inline_shapes[-1]._inline.docPr.set("descr", caption)
    doc.add_paragraph(caption, "Caption")


def table(headers, rows):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    for cell, text in zip(t.rows[0].cells, headers):
        cell.text = text
    for row in rows:
        for cell, text in zip(t.add_row().cells, row):
            cell.text = text
    for row in t.rows:
        row._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))
        for cell in row.cells:
            for para in cell.paragraphs:
                para.paragraph_format.space_after = Pt(4)
                for run in para.runs:
                    run.font.size = Pt(10)
    return t


doc.add_heading("Website Development", 0)
p("Unit 3 assignment report | Seventies Sound | 5 September 2026")
p("This is a three-page website introducing 1970s music to 17-23-year-olds. I used HTML, CSS and JavaScript. [1]")

doc.add_page_break()
doc.add_heading("Task 1: Research and planning", 1)
heading("Brief, audience and research")
p("The brief asks for a mobile-friendly three-page site with navigation, search, an accordion, video, image popups, external links, a request form and accessibility features. [1] I wanted the site to work for someone who knows a song already and someone who has never listened to 70s music.")
table(
    ["Site", "What I noticed", "What I used"],
    [
        ("TheGreat70s [2]", "The image makes the decade obvious, but the advert uses too much room on a phone.", "Clear heading and image, but no adverts."),
        ("ABBA [3]", "The dark layout and large image are strong. It mainly suits people who already know ABBA.", "Short introduction before a listening link."),
        ("Rock Hall [4]", "Artist cards and search make browsing easy. Its phone layout feels busy.", "Genre buttons and search, with one-column phone cards."),
    ],
)
p("The research screenshots are saved in planning-and-research/research-notes. ABBA's history gave me the 1974 Eurovision fact. I used David Bowie for glam rock and Donna Summer for disco, with official pages and chart information for facts and dates. [5-8]")
heading("Content, copyright and accessibility")
table(
    ["Decision", "Reason"],
    [
        ("Seven artists from different genres", "There is enough choice for a beginner, without making Explore hard to look through."),
        ("Official YouTube links and credited images", "This avoids copying music files. Source and licence records are kept with the assets. [9]"),
        ("Short request form", "It only asks for a topic, type of idea and optional reason. The visitor sends it from their own email app. [10, 11]"),
        ("Labels, alt text, captions and keyboard controls", "These make the content easier to use with a keyboard, screen reader or without sound. [12]"),
    ],
)
heading("Site map and page plan")
# Show the page structure and navigation flow with a simple palette.
im = Image.new("RGB", (1500, 900), "white")
draw = ImageDraw.Draw(im)
font_path = "/System/Library/Fonts/Supplemental/Arial.ttf"
bold_path = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
title_font = ImageFont.truetype(bold_path, 40)
heading_font = ImageFont.truetype(bold_path, 32)
body_font = ImageFont.truetype(font_path, 28)
small_font = ImageFont.truetype(font_path, 25)
accent = "black"
ink = "black"
green = "black"
card_fill = "white"

draw.rectangle((550, 35, 950, 125), fill=card_fill, outline=accent, width=3)
draw.text((625, 62), "Site navigation", font=heading_font, fill=ink)
draw.line((750, 125, 750, 175), fill=accent, width=4)

pages = [
    (55, "Home", "index.html", ["Intro and genre cards", "Timeline and video", "Captions and text version"]),
    (520, "Explore", "explore.html", ["Artists and songs", "Search and genre chips", "Accordions, photos and video"]),
    (985, "Request", "request.html", ["Suggestion form", "Email request only", "Privacy, credits, access"]),
]
for x, title, filename, notes in pages:
    draw.rectangle((x, 175, x + 410, 820), fill=card_fill, outline=accent, width=3)
    draw.text((x + 25, 215), title, font=title_font, fill=ink)
    draw.text((x + 25, 285), filename, font=body_font, fill=accent)
    draw.line((x + 25, 350, x + 385, 350), fill=accent, width=2)
    for index, note in enumerate(notes):
        draw.ellipse((x + 28, 405 + index * 105, x + 46, 423 + index * 105), fill=green)
        draw.text((x + 65, 393 + index * 105), note, font=small_font, fill=ink)

draw.line((260, 175, 260, 150, 1180, 150, 1180, 175), fill=accent, width=4)
draw.line((750, 125, 750, 150), fill=accent, width=4)
im.save(research / "site-map.png")
doc.add_picture(str(research / "site-map.png"), width=Inches(6.6))
doc.inline_shapes[-1]._inline.docPr.set(
    "descr", "Annotated site map showing shared navigation, page features and mobile behavior."
)
p(
    "The same navigation is used on every page. Explore has genre filters and search, and on phones the links open inside Menu."
)
table(
    ["Page", "Content and features"],
    [
        (
            "Home\nindex.html",
            "Introduction, genre cards, short timeline and video with captions and written text.",
        ),
        (
            "Explore\nexplore.html",
            "Artist cards, genre buttons, search, extra facts, larger photos and official listening links.",
        ),
        (
            "Request\nrequest.html",
            "Topic request form, privacy, credits and accessibility information.",
        ),
    ],
)
p("Home is the starting point, Explore has the music and Request is for suggestions. Search ignores capital letters and extra spaces. If there is no result, the genre buttons are still there to browse from.")


page("Sources")
p("Sources accessed on 5 September 2026.")
refs = [
    "[1] Pearson (2025), Unit 3: Website Development, supplied centre standardisation PDF. Client brief and Tasks 1-3: PDF pages 10-13. Distinction guidance: PDF page 57.",
    "[2] TheGreat70s, homepage. https://thegreat70s.com/",
    "[3] ABBA, official homepage. https://abbasite.com/",
    "[4] Rock & Roll Hall of Fame, artist directory. https://rockhall.com/inductees/inductees/",
    "[5] ABBA, The Story. https://abbasite.com/story/",
    "[6] ABBA, In Focus: Dancing Queen. https://abbasite.com/articles/dancing-queen/",
    "[7] Rock & Roll Hall of Fame, David Bowie. https://rockhall.com/inductees/david-bowie/",
    "[8] Official Charts, I Feel Love - Donna Summer. https://www.officialcharts.com/songs/donna-summer-i-feel-love/",
    "[9] GOV.UK, Using somebody else's intellectual property: Copyright. https://www.gov.uk/using-somebody-elses-intellectual-property/copyright",
    "[10] ICO, Cookies and privacy notices in detail. Guidance marked under review. https://ico.org.uk/for-organisations/advice-for-small-organisations/privacy-notices-and-cookies/cookies-and-privacy-notices-in-detail/",
    "[11] ICO, Children and the UK GDPR. https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/childrens-information/children-and-the-uk-gdpr/",
    "[12] W3C, How to Meet WCAG 2.2. https://www.w3.org/WAI/WCAG22/quickref/",
]
for ref in refs:
    para = p(ref)
    for run in para.runs:
        run.font.size = Pt(10)

# Straight punctuation throughout, including any later edits to the text above.
for para in doc.paragraphs:
    for run in para.runs:
        if run.text:
            run.text = run.text.translate(
                str.maketrans(
                    {
                        "\u2018": "'",
                        "\u2019": "'",
                        "\u201c": '"',
                        "\u201d": '"',
                        "\u2014": " - ",
                        "\u2013": "-",
                    }
                )
            )
doc.core_properties.title = "Website Development - Assignment report"
doc.core_properties.author = ""
if (root.parent / "website-design/website/screenshots/home-sheet.png").exists():
    from task2_report import add_task2

    add_task2(doc)
if (root.parent / "website-testing/test-results/functional-results.json").exists():
    from task3_report import add_task3

    add_task3(doc)
doc.save(report_folder / "Website development report.docx")
print("Report rebuilt.")
