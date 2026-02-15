import { jsPDF } from "jspdf";
import autoTable from "jspdf-autotable";

export const generarReportePDF = (incidencias, subprograma, fechaInicio, fechaFin) => {
    const doc = new jsPDF('l', 'mm', 'a4'); // Cambiado a horizontal (landscape) para que quepa todo bien
    const fechaGen = new Date().toLocaleString();

    doc.setFontSize(18);
    doc.setTextColor(225, 29, 72);
    doc.text("REPORTE GLOBAL DE INCIDENCIAS", 14, 20);

    doc.setFontSize(10);
    doc.setTextColor(100);
    doc.text(`Subprograma: ${subprograma}`, 14, 28);
    doc.text(`Periodo: ${fechaInicio} hasta ${fechaFin}`, 14, 33);
    doc.text(`Generado el: ${fechaGen}`, 14, 38);

    const columns = [
        { header: 'ID', dataKey: 'id' },
        { header: 'TIPO DE INCIDENCIA', dataKey: 'tipo' },
        { header: 'ESTADO ACTUAL', dataKey: 'estado' }, // Columna de estado
        { header: 'SOLICITANTE', dataKey: 'persona' },
        { header: 'C.I.', dataKey: 'ci' },
        { header: 'FECHA REGISTRO', dataKey: 'fecha' }
    ];

    const rows = incidencias.map(inc => ({
        id: `#${inc.id}`,
        tipo: (inc.tipo_incidencia || '').replace(/_/g, ' '),
        estado: inc.estado, // Se asegura de tomar el estado
        persona: `${inc.persona?.nombre || 'N/A'} ${inc.persona?.apellido || ''}`,
        ci: inc.persona?.ci || '---',
        fecha: new Date(inc.fecha_creacion).toLocaleDateString('es-ES')
    }));

    autoTable(doc, {
        startY: 45,
        columns: columns,
        body: rows,
        theme: 'striped',
        headStyles: { fillColor: [225, 29, 72], textColor: 255, fontSize: 9, fontStyle: 'bold' },
        styles: { fontSize: 8, cellPadding: 3 },
        columnStyles: {
            id: { cellWidth: 15 },
            estado: { fontStyle: 'bold' } // Resaltar el estado
        }
    });

    doc.save(`Reporte_Global_${subprograma}.pdf`);
};