import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT


def generate_invoice_pdf(order, invoice, business) -> io.BytesIO:
    """
    Generate a styled invoice PDF for a given order.

    Args:
        order:    ORM Order object (with .items loaded)
        invoice:  ORM Invoice object (or None)
        business: ORM BusinessProfile object (or None)

    Returns:
        io.BytesIO buffer containing the PDF bytes (seeked to 0).
    """

    
    biz_name   = getattr(business, "business_name", None) or "ElectroMart"
    biz_addr   = getattr(business, "address",       None) or ""
    biz_phone  = getattr(business, "phone",         None) or ""
    biz_email  = getattr(business, "email",         None) or ""
    biz_gst    = getattr(business, "gst_number",    None) or ""
    gst_rate   = getattr(business, "gst_percentage",None) or 18.0

    styles = getSampleStyleSheet()

    
    def ps(name, **kwargs):
        """Shortcut: create a named ParagraphStyle."""
        return ParagraphStyle(name, **kwargs)

    INDIGO  = colors.HexColor("#4F46E5")
    GRAY    = colors.HexColor("#6B7280")
    LIGHT   = colors.HexColor("#E5E7EB")
    GREEN   = colors.HexColor("#16A34A")
    RED     = colors.HexColor("#DC2626")
    ROW_ALT = colors.HexColor("#F8F8F8")

    
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=2 * cm, leftMargin=2 * cm,
        topMargin=2 * cm,   bottomMargin=2 * cm,
    )
    elements = []

    # ── Header: business name + invoice meta ─────────────────
    inv_number = invoice.invoice_number if invoice else "N/A"
    inv_date   = order.created_at.strftime("%d %b %Y")

    header_data = [[
        Paragraph(
            f"<b>{biz_name}</b>",
            ps("biz_name", fontSize=18, fontName="Helvetica-Bold", textColor=INDIGO),
        ),
        Paragraph(
            f"<b>INVOICE</b><br/>"
            f"<font size=9>No: {inv_number}</font><br/>"
            f"<font size=9>Date: {inv_date}</font>",
            ps("inv_meta", fontSize=14, fontName="Helvetica-Bold", alignment=TA_RIGHT),
        ),
    ]]
    header_table = Table(header_data, colWidths=[9.5 * cm, 9.5 * cm])
    header_table.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    elements.append(header_table)

    # Business contact details
    biz_details = []
    if biz_addr:  biz_details.append(biz_addr)
    if biz_phone: biz_details.append(f"Phone: {biz_phone}")
    if biz_email: biz_details.append(f"Email: {biz_email}")
    if biz_gst:   biz_details.append(f"GST: {biz_gst}")

    for detail in biz_details:
        elements.append(Paragraph(
            detail,
            ps("biz_detail", fontSize=9, textColor=GRAY, spaceBefore=1),
        ))

    elements.append(Spacer(1, 0.4 * cm))
    elements.append(HRFlowable(width="100%", thickness=1, color=LIGHT))
    elements.append(Spacer(1, 0.4 * cm))

    
    inv_status      = invoice.status if invoice else "unpaid"
    status_color    = GREEN if inv_status == "paid" else RED

    bill_data = [
        [
            Paragraph("<b>Bill To:</b>",        ps("bt_label", fontSize=10, fontName="Helvetica-Bold")),
            Paragraph("<b>Payment Status:</b>", ps("ps_label", fontSize=10, fontName="Helvetica-Bold", alignment=TA_RIGHT)),
        ],
        [
            Paragraph(order.customer_name, ps("cust_name", fontSize=10)),
            Paragraph(
                inv_status.upper(),
                ps("inv_status", fontSize=10, alignment=TA_RIGHT, textColor=status_color),
            ),
        ],
    ]
    if order.customer_phone:
        bill_data.append([
            Paragraph(
                f"Phone: {order.customer_phone}",
                ps("cust_phone", fontSize=9, textColor=GRAY),
            ),
            Paragraph("", styles["Normal"]),
        ])

    bill_table = Table(bill_data, colWidths=[9.5 * cm, 9.5 * cm])
    bill_table.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    elements.append(bill_table)
    elements.append(Spacer(1, 0.5 * cm))

    
    subtotal    = sum(item.unit_price * item.quantity for item in order.items)
    gst_amount  = round(subtotal * gst_rate / 100, 2)
    grand_total = round(subtotal + gst_amount, 2)

    # Header row
    table_data = [[
        Paragraph("<b>Product</b>",    ps("th", fontSize=10, fontName="Helvetica-Bold", textColor=colors.white)),
        Paragraph("<b>Qty</b>",        ps("th_c", fontSize=10, fontName="Helvetica-Bold", textColor=colors.white, alignment=TA_CENTER)),
        Paragraph("<b>Unit Price</b>", ps("th_r", fontSize=10, fontName="Helvetica-Bold", textColor=colors.white, alignment=TA_RIGHT)),
        Paragraph("<b>Total</b>",      ps("th_r2", fontSize=10, fontName="Helvetica-Bold", textColor=colors.white, alignment=TA_RIGHT)),
    ]]

    
    for item in order.items:
        name       = item.product.name if item.product else f"Product #{item.product_id}"
        line_total = item.unit_price * item.quantity
        table_data.append([
            Paragraph(name,                            ps("td",   fontSize=10)),
            Paragraph(str(item.quantity),              ps("td_c", fontSize=10, alignment=TA_CENTER)),
            Paragraph(f"Rs. {item.unit_price:,.2f}",   ps("td_r", fontSize=10, alignment=TA_RIGHT)),
            Paragraph(f"Rs. {line_total:,.2f}",        ps("td_r2",fontSize=10, alignment=TA_RIGHT)),
        ])

    n = len(order.items)  # number of item rows (excluding header)

    # Subtotal / GST / Grand Total rows
    empty = Paragraph("", styles["Normal"])
    table_data.append([
        empty, empty,
        Paragraph("Subtotal",              ps("sub",  fontSize=10, alignment=TA_RIGHT)),
        Paragraph(f"Rs. {subtotal:,.2f}", ps("sub_v",fontSize=10, alignment=TA_RIGHT)),
    ])
    table_data.append([
        empty, empty,
        Paragraph(
            f"GST ({gst_rate:.0f}%)",
            ps("gst_l", fontSize=10, alignment=TA_RIGHT, textColor=GRAY),
        ),
        Paragraph(
            f"Rs. {gst_amount:,.2f}",
            ps("gst_v", fontSize=10, alignment=TA_RIGHT, textColor=GRAY),
        ),
    ])
    table_data.append([
        empty, empty,
        Paragraph("<b>Total</b>",                  ps("tot_l",fontSize=11, fontName="Helvetica-Bold", alignment=TA_RIGHT)),
        Paragraph(f"<b>Rs. {grand_total:,.2f}</b>",ps("tot_v",fontSize=11, fontName="Helvetica-Bold", alignment=TA_RIGHT)),
    ])

    items_table = Table(table_data, colWidths=[9 * cm, 2 * cm, 4 * cm, 4 * cm])
    items_table.setStyle(TableStyle([
        # Header background
        ("BACKGROUND",    (0, 0),    (-1, 0),    INDIGO),
        # Alternating item rows
        ("ROWBACKGROUNDS",(0, 1),    (-1, n),    [colors.white, ROW_ALT]),
        # Summary rows — plain white
        ("BACKGROUND",    (0, n + 1),(-1, -1),   colors.white),
        # Divider above subtotal
        ("LINEABOVE",     (0, n + 1),(-1, n + 1),1,   LIGHT),
        # Stronger divider above grand total
        ("LINEABOVE",     (0, -1),   (-1, -1),   1.5, INDIGO),
        # Grid on header + item rows only
        ("GRID",          (0, 0),    (-1, n),    0.5, LIGHT),
        ("VALIGN",        (0, 0),    (-1, -1),   "MIDDLE"),
        ("BOTTOMPADDING", (0, 0),    (-1, -1),   8),
        ("TOPPADDING",    (0, 0),    (-1, -1),   8),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 1 * cm))


    elements.append(HRFlowable(width="100%", thickness=0.5, color=LIGHT))
    elements.append(Spacer(1, 0.3 * cm))
    elements.append(Paragraph(
        f"Thank you for shopping at {biz_name}!",
        ps("footer", fontSize=9, textColor=GRAY, alignment=TA_CENTER),
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer