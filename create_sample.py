from fpdf import FPDF
from fpdf.enums import XPos, YPos

# --- Helper function to create a clean page layout ---
def setup_page(pdf):
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_fill_color(240, 240, 240)
    
    # Header
    pdf.cell(0, 10, "St. Jude's Medical Center", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, "123 Health Drive, Meditown, USA", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 6, "Phone: (123) 456-7890 | Fax: (123) 456-7891", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    # Title
    pdf.ln(10) # Add a line break
    pdf.set_font("Helvetica", "BU", 14)
    pdf.cell(0, 10, "PATHOLOGY & LAB REPORT", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(5)

# --- Helper function for section titles ---
def add_section_title(pdf, title):
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_fill_color(220, 220, 220)
    pdf.cell(0, 8, title, align="L", fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(4)

# --- Helper function for key-value pairs ---
def add_info_pair(pdf, key, value):
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(40, 6, key, align="L", new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, value, align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

# --- Helper function for table headers ---
def add_table_header(pdf):
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(60, 7, "Test Name", border=1, align="C", new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.cell(40, 7, "Result", border=1, align="C", new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.cell(40, 7, "Flag", border=1, align="C", new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.cell(50, 7, "Reference Range", border=1, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

# --- Helper function for table rows ---
def add_table_row(pdf, test, result, flag, ref):
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(60, 7, test, border=1, align="L", new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.cell(40, 7, result, border=1, align="C", new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(40, 7, flag, border=1, align="C", new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(50, 7, ref, border=1, align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

# ===============================================
# --- MAIN SCRIPT TO CREATE THE PDF ---
# ===============================================

pdf = FPDF()
setup_page(pdf)

# --- Patient Information Section ---
add_section_title(pdf, "Patient Information")
add_info_pair(pdf, "Patient Name:", "Doe, John A.")
add_info_pair(pdf, "Patient ID:", "JD45-6789")
add_info_pair(pdf, "Date of Birth:", "10/24/1985 (Age: 40)")
add_info_pair(pdf, "Gender:", "Male")
add_info_pair(pdf, "Referring MD:", "Dr. Evelyn Reed")

# --- Specimen Information Section ---
add_section_title(pdf, "Specimen Information")
add_info_pair(pdf, "Specimen ID:", "BL-98765")
add_info_pair(pdf, "Specimen Type:", "Whole Blood (Lavender Top)")
add_info_pair(pdf, "Date Collected:", "2025-10-23 09:15:00")
add_info_pair(pdf, "Date Received:", "2025-10-23 10:30:00")
pdf.ln(5)

# --- Results Section - Complete Blood Count (CBC) ---
add_section_title(pdf, "Complete Blood Count (CBC)")
add_table_header(pdf)
add_table_row(pdf, "White Blood Cell (WBC) Count", "13.5", "HIGH", "4.0 - 11.0 x10^9/L")
add_table_row(pdf, "Red Blood Cell (RBC) Count", "4.80", "", "4.20 - 5.80 x10^12/L")
add_table_row(pdf, "Hemoglobin (HGB)", "15.1", "", "13.5 - 17.5 g/dL")
add_table_row(pdf, "Hematocrit (HCT)", "45.0", "", "40.0 - 50.0 %")
add_table_row(pdf, "Platelet Count", "145", "LOW", "150 - 450 x10^9/L")
add_table_row(pdf, "Neutrophils", "75", "HIGH", "40 - 70 %")
add_table_row(pdf, "Lymphocytes", "18", "LOW", "20 - 45 %")
pdf.ln(5)

# --- Pathologist's Diagnosis/Comments ---
add_section_title(pdf, "Pathologist's Summary & Diagnosis")
pdf.set_font("Helvetica", "", 10)
pdf.multi_cell(0, 6, 
    "CLINICAL HISTORY: Patient presents with a 3-day history of fever, fatigue, and persistent cough. "
    "Referred for bloodwork to rule out infection.\n\n"
    "DIAGNOSIS: **Leukocytosis with neutrophilia and mild thrombocytopenia.**\n\n"
    "COMMENTS: The elevated White Blood Cell count with a high percentage of neutrophils (neutrophilia) "
    "is strongly indicative of an active bacterial infection. The low platelet count (thrombocytopenia) "
    "is mild but should be monitored. Correlation with clinical findings and C-Reactive Protein (CRP) levels "
    "is recommended. Patient's reported symptoms (fever, cough) are consistent with these findings."
)
pdf.ln(10)

# --- Footer / Signature ---
pdf.set_font("Helvetica", "I", 10)
pdf.cell(0, 10, "Electronically Signed By:", align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.set_font("Helvetica", "B", 10)
pdf.cell(0, 6, "Dr. David Chen, MD (Pathologist-in-Chief)", align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.set_font("Helvetica", "", 10)
pdf.cell(0, 6, "Report Date: 2025-10-24 00:30:00", align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.cell(0, 6, "*** END OF REPORT ***", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

# --- Save the file ---
pdf.output("sample_medical_report.pdf")

print("Successfully created 'sample_medical_report.pdf'!")