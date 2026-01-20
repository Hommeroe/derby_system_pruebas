# --- FUNCIÓN DE PDF ACTUALIZADA (IMPRESIÓN EN BLANCO Y LOGO BICOLOR) ---
def generar_pdf(partidos, n_gallos):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=30, rightMargin=30, topMargin=30, bottomMargin=30)
    elements = []
    styles = getSampleStyleSheet()
    
    zona_horaria = pytz.timezone('America/Mexico_City')
    ahora = datetime.now(zona_horaria).strftime("%d/%m/%Y %H:%M:%S")
    
    # Nuevo diseño de encabezado: Fondo blanco y texto bicolor
    data_header = [
        [Paragraph("<font color='black' size=26><b>DERBY</b></font><font color='#E67E22' size=26><b>System</b></font>", styles['Title'])],
        [Paragraph(f"<font color='#333' size=10><b>REPORTE OFICIAL DE COTEJO</b></font>", styles['Normal'])],
        [Paragraph(f"<font color='grey' size=8>Mesa de Control: {st.session_state.id_usuario} | Generado el: {ahora}</font>", styles['Normal'])]
    ]
    
    header_table = Table(data_header, colWidths=[500])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white), # Fondo quitado (ahora blanco)
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 20))

    for r in range(1, n_gallos + 1):
        elements.append(Paragraph(f"<b>RONDA {r}</b>", styles['Heading2']))
        elements.append(Spacer(1, 8))
        
        col_g = f"G{r}"
        lista = sorted([dict(p) for p in partidos], key=lambda x: x[col_g])
        data = [["#", "G", "PARTIDO (ROJO)", "AN.", "E", "DIF.", "AN.", "PARTIDO (VERDE)", "G"]]
        
        pelea_n = 1
        while len(lista) >= 2:
            rojo = lista.pop(0)
            v_idx = next((i for i, x in enumerate(lista) if limpiar_nombre_socio(x["PARTIDO"]) != limpiar_nombre_socio(rojo["PARTIDO"])), None)
            
            if v_idx is not None:
                verde = lista.pop(v_idx)
                d = abs(rojo[col_g] - verde[col_g])
                idx_r = next(i for i, p in enumerate(partidos) if p["PARTIDO"]==rojo["PARTIDO"])
                idx_v = next(i for i, p in enumerate(partidos) if p["PARTIDO"]==verde["PARTIDO"])
                an_r, an_v = (idx_r * n_gallos) + r, (idx_v * n_gallos) + r
                
                data.append([
                    pelea_n, "[  ]", 
                    Paragraph(f"<b>{rojo['PARTIDO']}</b><br/><font size=8>({rojo[col_g]:.3f})</font>", styles['Normal']),
                    f"{an_r:03}", "[  ]", f"{d:.3f}", f"{an_v:03}", 
                    Paragraph(f"<b>{verde['PARTIDO']}</b><br/><font size=8>({verde[col_g]:.3f})</font>", styles['Normal']),
                    "[  ]"
                ])
                pelea_n += 1
            else: break
        
        t = Table(data, colWidths=[20, 30, 140, 30, 30, 40, 30, 140, 30])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1a1a1a")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#E67E22")),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LINEBEFORE', (2,1), (2,-1), 2, colors.red),
            ('LINEAFTER', (7,1), (7,-1), 2, colors.green),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 20))
    
    # Sección de firmas
    elements.append(Spacer(1, 40))
    data_firmas = [
        ["__________________________", " ", "__________________________"],
        ["FIRMA JUEZ DE PLAZA", " ", "FIRMA MESA DE CONTROL"]
    ]
    t_firmas = Table(data_firmas, colWidths=[200, 100, 200])
    t_firmas.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
    ]))
    elements.append(t_firmas)
    
    doc.build(elements)
    return buffer.getvalue()
