def generar_pdf(partidos, n_gallos):
    buffer = BytesIO()
    # Márgenes ajustados para dar buen espacio de escritura
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=30, rightMargin=30, topMargin=30, bottomMargin=30)
    elements = []
    styles = getSampleStyleSheet()
    
    # --- ENCABEZADO ESTILO "DERBY SYSTEM" ---
    data_header = [
        [Paragraph("<font color='white' size=16><b>DERBYsystem</b></font>", styles['Title'])],
        [Paragraph(f"<font color='#E67E22' size=10>REPORTE OFICIAL DE COTEJO: {st.session_state.id_usuario}</font>", styles['Normal'])]
    ]
    header_table = Table(data_header, colWidths=[500])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.black),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor("#1a1a1a")),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 20))

    # --- CUERPO DEL COTEJO POR RONDAS ---
    for r in range(1, n_gallos + 1):
        elements.append(Paragraph(f"<b>RONDA {r}</b>", styles['Heading2']))
        elements.append(Spacer(1, 8))
        
        col_g = f"G{r}"
        lista = sorted([dict(p) for p in partidos], key=lambda x: x[col_g])
        
        # Encabezados de la tabla
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
                
                # Se agregan los [  ] en las columnas de G y E
                data.append([
                    pelea_n, 
                    "[  ]", # G Rojo
                    Paragraph(f"<b>{rojo['PARTIDO']}</b><br/><font size=8>({rojo[col_g]:.3f})</font>", styles['Normal']),
                    f"{an_r:03}", 
                    "[  ]", # Empate
                    f"{d:.3f}", 
                    f"{an_v:03}", 
                    Paragraph(f"<b>{verde['PARTIDO']}</b><br/><font size=8>({verde[col_g]:.3f})</font>", styles['Normal']),
                    "[  ]"  # G Verde
                ])
                pelea_n += 1
            else:
                break
        
        # Estilo de la tabla de peleas
        t = Table(data, colWidths=[20, 30, 140, 30, 30, 40, 30, 140, 30])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1a1a1a")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#E67E22")),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            # Líneas de color para distinguir lados
            ('LINEBEFORE', (2,1), (2,-1), 2, colors.red),
            ('LINEAFTER', (7,1), (7,-1), 2, colors.green),
            # Sombreado ligero para las columnas de marcar (G y E)
            ('BACKGROUND', (1,1), (1,-1), colors.whitesmoke),
            ('BACKGROUND', (4,1), (4,-1), colors.whitesmoke),
            ('BACKGROUND', (8,1), (8,-1), colors.whitesmoke),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 20))
    
    # Pie de página
    elements.append(Spacer(1, 30))
    elements.append(Paragraph("<font color='grey' size=8>Documento para uso en mesa. Marque con [X] el resultado de cada combate.</font>", styles['Normal']))
    
    doc.build(elements)
    return buffer.getvalue()
