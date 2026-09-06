from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

root = Path(__file__).resolve().parents[1] / "website-design"
font_path = "/System/Library/Fonts/Supplemental/Arial.ttf"
bold_path = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"


def font(size, bold=False):
    return ImageFont.truetype(bold_path if bold else font_path, size)


def label(draw, xy, text, size=25):
    draw.multiline_text(xy, text, font=font(size), fill="#29231e", spacing=9)


def box(draw, rect, text, size=25):
    draw.rectangle(rect, fill="#f3f3f3", outline="#555555", width=2)
    label(draw, (rect[0] + 14, rect[1] + 14), text, size)


for page in ("home", "explore", "request"):
    im = Image.new("RGB", (1450, 1250), "white")
    d = ImageDraw.Draw(im)
    label(d, (25, 18), page.title() + " wireframe", 38)
    label(d, (25, 80), "Desktop: 1280px wide", 25)
    label(d, (1030, 80), "Phone: 390px wide", 25)
    box(
        d,
        (25, 135, 960, 215),
        "Logo                 Home   Explore v   Request       Search",
    )
    box(d, (1030, 135, 1420, 240), "Logo                  Menu\nSearch", 24)
    if page == "home":
        box(
            d,
            (25, 240, 580, 490),
            "Main heading\nShort introduction\n[Explore music]",
            29,
        )
        box(d, (610, 240, 960, 490), "Record image", 27)
        for x, t in [(25, "Pop"), (345, "Glam rock"), (665, "Disco")]:
            box(d, (x, 520, x + 295, 755), "Image\n" + t + "\n[Explore genre]")
        box(d, (25, 785, 470, 990), "Timeline\n1974 - ABBA\n1977 - Donna Summer")
        box(d, (500, 785, 960, 990), "Video + controls\nCaptions\nWritten video text")
        for y, height, t in [
            (265, 190, "Heading + intro\n[Explore music]"),
            (480, 160, "Record image"),
            (665, 110, "Pop card"),
            (800, 110, "Glam rock card"),
            (935, 110, "Disco card"),
        ]:
            box(d, (1030, y, 1420, y + height), t, 24)
        note = "Phone continues: timeline, video and footer.\nTitle and Explore button come before the image.\nDesktop cards align in three equal columns; phone cards stack."
    elif page == "explore":
        box(
            d,
            (25, 240, 960, 370),
            "Heading + introduction\n[All music] [Pop] [Glam rock] [Disco]",
        )
        for y, n in [
            (400, "ABBA / Pop"),
            (620, "David Bowie / Glam rock"),
            (840, "Donna Summer / Disco"),
        ]:
            box(d, (25, y, 300, y + 190), "Image\n[Enlarge]")
            box(
                d,
                (330, y, 960, y + 190),
                n
                + "\nIntro + song / year + [Play]\n[More about music v] / Source / Request",
                24,
            )
        for y, height, t in [
            (265, 150, "Heading + intro\nGenre choices"),
            (440, 220, "Artist image\n[Enlarge image]"),
            (685, 120, "Artist + intro / song / Play"),
            (830, 90, "[More about music v]"),
            (945, 100, "Source / Request more"),
        ]:
            box(d, (1030, y, 1420, y + height), t, 24)
        note = "Phone repeats the artist layout for the remaining genres.\nPlay loads the video inside the page; a YouTube link is also available.\nImage opens in a popup; accordion adds detail without another page."
    else:
        box(d, (25, 240, 960, 350), "Heading\nBrief explanation")
        box(
            d,
            (25, 380, 585, 980),
            "Topic *\n[Text field]\nContent type *\n[Drop-down]\nAnything else?\n[Text area]\n[Send request]\nRequired field errors",
            27,
        )
        box(
            d,
            (615, 380, 960, 730),
            "Request guidance\n\nNo personal details\nneeded\n\nPrivacy link",
            25,
        )
        box(d, (615, 760, 960, 980), "Privacy\nCredits\nAccessibility", 25)
        for y, height, t in [
            (265, 120, "Heading + intro"),
            (
                410,
                410,
                "Topic *\n[Text field]\nContent type *\n[Drop-down]\nAnything else?\n[Text area]\n[Send request]",
            ),
            (850, 195, "Guidance\nPrivacy / Credits\nAccessibility"),
        ]:
            box(d, (1030, y, 1420, y + height), t, 24)
        note = "Phone form stays in one column, with labels above fields.\nRequired fields are marked; errors sit beside the relevant field.\nEmail app opens with the request; the visitor sends it."
    label(d, (25, 1090), note, 25)
    im.save(root / "page-plans" / f"{page}.png")
im = Image.new("RGB", (1450, 720), "white")
d = ImageDraw.Draw(im)
label(d, (30, 25), "Seventies Sound - visual style", 38)
for x, name, c in [
    (30, "Page background", "#F7F1E5"),
    (375, "Text", "#29231E"),
    (720, "Main buttons", "#934326"),
    (1065, "Selected genre", "#345B50"),
]:
    d.rectangle((x, 100, x + 305, 240), fill=c)
    label(d, (x, 260), name + "\n" + c, 25)
label(d, (30, 365), "Headings: Georgia bold", 34)
label(d, (30, 425), "Body text and controls: Arial", 29)
label(
    d, (30, 485), "Desktop title: 58px / phone: 38px     Body: 17px / phone: 16px", 25
)
label(
    d,
    (30, 545),
    "Same header and buttons on all pages. Cards line up with the content edges.",
    25,
)
label(
    d,
    (30, 600),
    "Controls have text labels. Colour is not the only way to show errors or selection.",
    25,
)
im.save(root / "website/screenshots/style-sheet.png")
print("Wireframes and style sheet ready.")
