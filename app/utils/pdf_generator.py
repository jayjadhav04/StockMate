import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from app.models.sale import Sale

def generate_invoice_pdf(sale: Sale, buffer: io.BytesIO):
    """
    Generates a professional PDF invoice using ReportLab flowables.
    Writes the PDF bytes into the provided BytesIO buffer.
    """
    # 1. Initialize Document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # 2. Define Styles
    title_style = ParagraphStyle(
        'CompanyTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#0f172a')
    )
    
    subtitle_style = ParagraphStyle(
        'CompanySubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#64748b')
    )
    
    heading_style = ParagraphStyle(
        'InvoiceHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#3b82f6')
    )
    
    bold_label_style = ParagraphStyle(
        'BoldLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#1e293b')
    )
    
    normal_text_style = ParagraphStyle(
        'NormalText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155')
    )
    
    th_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=12,
        textColor=colors.white
    )
    
    td_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#0f172a')
    )

    # 3. Add Header Section (Company Name on Left, "INVOICE" details on Right)
    company_info = [
        Paragraph("StockMate Ltd.", title_style),
        Paragraph("123 Business Avenue, Suite 500", subtitle_style),
        Paragraph("Phone: +1 555-0199 | Email: info@stockmate.com", subtitle_style)
    ]
    
    invoice_info = [
        Paragraph("INVOICE", heading_style),
        Paragraph(f"<b>Invoice #:</b> {sale.invoice_number}", normal_text_style),
        Paragraph(f"<b>Date:</b> {sale.sale_date.strftime('%Y-%m-%d %H:%M')}", normal_text_style),
        Paragraph(f"<b>Billed By:</b> {sale.employee.full_name}", normal_text_style),
        Paragraph(f"<b>Payment:</b> {getattr(sale, 'payment_method', 'Cash')}", normal_text_style)
    ]
    
    header_table_data = [
        [company_info, invoice_info]
    ]
    
    header_table = Table(header_table_data, colWidths=[300, 240])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('PADDING', (0,0), (-1,-1), 0),
    ]))
    
    story.append(header_table)
    story.append(Spacer(1, 20))
    
    # 4. Add Customer Section
    cust = sale.customer
    customer_details = [
        Paragraph("<b>BILLED TO:</b>", bold_label_style),
        Paragraph(cust.customer_name, bold_label_style),
        Paragraph(f"Phone: {cust.phone}", normal_text_style),
        Paragraph(f"Email: {cust.email}", normal_text_style),
        Paragraph(f"Address: {cust.address}", normal_text_style)
    ]
    
    customer_table = Table([[customer_details]], colWidths=[540])
    customer_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#e2e8f0')),
        ('PADDING', (0,0), (-1,-1), 12),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    
    story.append(customer_table)
    story.append(Spacer(1, 20))

    # 5. Add Products Table
    table_data = [
        # Table Headers
        [
            Paragraph("S.No", th_style), 
            Paragraph("Product Name", th_style), 
            Paragraph("Quantity", th_style), 
            Paragraph("Unit Price", th_style), 
            Paragraph("Subtotal", th_style)
        ]
    ]
    
    # Table rows
    for i, item in enumerate(sale.items, start=1):
        table_data.append([
            Paragraph(str(i), td_style),
            Paragraph(item.product.product_name, td_style),
            Paragraph(str(item.quantity), td_style),
            Paragraph(f"₹{item.selling_price:.2f}", td_style),
            Paragraph(f"₹{item.line_total:.2f}", td_style)
        ])
        
    # Table layout width: total 540 (matches printable area)
    col_widths = [40, 240, 70, 90, 100]
    
    products_table = Table(table_data, colWidths=col_widths)
    products_table_style = [
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e293b')), # Slate table header
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,0), 10),
        ('TOPPADDING', (0,0), (-1,0), 10),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
    ]
    
    # Alternate row background styling
    for r in range(1, len(table_data)):
        if r % 2 == 0:
            products_table_style.append(('BACKGROUND', (0,r), (-1,r), colors.HexColor('#f8fafc')))
            
    products_table.setStyle(TableStyle(products_table_style))
    story.append(products_table)
    story.append(Spacer(1, 15))

    # 6. Add GST Breakdown & Grand Total
    total_gst = getattr(sale, 'total_gst', 0.0) or 0.0
    grand_total = sale.total_amount + total_gst
    totals_data = [
        ["", Paragraph("Subtotal (ex-GST):", bold_label_style), Paragraph(f"₹{sale.total_amount:.2f}", bold_label_style)],
        ["", Paragraph("GST:", bold_label_style), Paragraph(f"₹{total_gst:.2f}", bold_label_style)],
        ["", Paragraph("<b>Grand Total:</b>", bold_label_style), Paragraph(f"<b>₹{grand_total:.2f}</b>", bold_label_style)]
    ]
    totals_table = Table(totals_data, colWidths=[340, 110, 90])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
        ('PADDING', (0,0), (-1,-1), 6),
        ('LINEABOVE', (1,2), (2,2), 1, colors.HexColor('#3b82f6')),
        ('BACKGROUND', (1,2), (2,2), colors.HexColor('#eff6ff')),  # highlight grand total
        ('BOX', (1,2), (2,2), 1, colors.HexColor('#3b82f6')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(totals_table)
    story.append(Spacer(1, 30))

    # 7. Add Thank You Footer
    footer_text = Paragraph("Thank you for your business! If you have any questions, please contact our support.", subtitle_style)
    footer_table = Table([[footer_text]], colWidths=[540])
    footer_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('PADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(footer_table)

    # Build PDF doc
    doc.build(story)
