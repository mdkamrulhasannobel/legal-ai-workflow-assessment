"""Generate synthetic messy legal PDFs for demonstration."""
import os
from pathlib import Path

from fpdf import FPDF

OUTPUT_DIR = Path(__file__).parent.parent / "data" / "sample_inputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def sample_1_contract_scan():
    """Blurry, skewed contract that would need OCR."""
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()

    pdf.set_font("Courier", size=10)
    pdf.set_draw_color(200, 200, 200)
    for _ in range(3):
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(1)

    pdf.set_font("Times", "B", 16)
    pdf.cell(0, 10, "SERVICE AGREEMENT", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(5)

    pdf.set_font("Times", "", 11)
    pdf.multi_cell(0, 6, (
        "This SERVICE AGREEMENT (the \"Agreement\") is made and entered into on "
        "January 15, 2024, by and between:\n\n"
        "Pearson Specter Litt LLP, a New York limited liability partnership "
        "(\"Firm\"), and\n"
        "GlobalCorp Industries Inc., a Delaware corporation (\"Client\").\n\n"
        "WHEREAS, Client desires to retain the Firm to provide legal services "
        "in connection with the merger acquisition of ZenTech Solutions;\n\n"
        "WHEREAS, the Firm has the expertise and resources to provide such services;\n\n"
        "NOW, THEREFORE, in consideration of the mutual covenants contained herein, "
        "the parties agree as follows:\n\n"
        "1. SCOPE OF SERVICES. The Firm shall provide legal representation and "
        "counseling regarding the merger, including due diligence review, "
        "contract negotiation, and regulatory compliance assessment.\n\n"
        "2. FEES AND EXPENSES. The Client shall pay the Firm an hourly rate of "
        "$850 for partner time, $450 for associate time, and $200 for paralegal time. "
        "A retainer of $100,000 shall be paid upon execution of this Agreement.\n\n"
        "3. CONFIDENTIALITY. The Firm shall maintain strict confidentiality regarding "
        "all client matters under the terms of the New York Rules of Professional Conduct.\n\n"
        "4. TERMINATION. Either party may terminate this Agreement upon 30 days written notice.\n\n"
        "5. GOVERNING LAW. This Agreement shall be governed by the laws of the State of New York.\n\n"
        "IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first written above.\n\n"
        "__________________________          __________________________\n"
        "Harvey Specter, Managing Partner      James Callis, CEO, GlobalCorp Industries\n"
        "Pearson Specter Litt LLP"
    ))
    pdf.ln(5)
    pdf.set_font("Times", "I", 8)
    pdf.multi_cell(0, 4, "Document scanned on 2024-01-20 | Quality: Standard")
    path = OUTPUT_DIR / "contract_scan.pdf"
    pdf.output(str(path))
    print(f"Created: {path}")


def sample_2_case_brief():
    """Text-layer PDF with inconsistent formatting."""
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Case Brief: Pearson Specter Litt v. GlobalCorp Industries", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 5, (
        "Case No. 24-CV-0789 | Southern District of New York\n"
        "Filed: March 12, 2024 | Judge: Hon. Sarah Mitchell\n\n"
        "PARTIES:\n"
        "Plaintiff:  Pearson Specter Litt LLP, 1250 Avenue of the Americas, New York, NY 10020\n"
        "Defendant:  GlobalCorp Industries Inc., 1 Corporate Drive, Wilmington, DE 19801\n\n"
        "STATEMENT OF FACTS:\n"
        "On or about January 15, 2024, Plaintiff and Defendant entered into a Service Agreement "
        "(the \"Agreement\") wherein Plaintiff agreed to provide legal services related to the "
        "acquisition of ZenTech Solutions by Defendant.\n\n"
        "Plaintiff performed substantial work in accordance with the Agreement, including:\n"
        "- Due diligence review of 15,000+ documents\n"
        "- Negotiation of merger terms with ZenTech stakeholders\n"
        "- Preparation of regulatory filings with the SEC and FTC\n\n"
        "Despite repeated demands, Defendant has failed to pay outstanding invoices totaling "
        "$347,850 for services rendered between January and March 2024.\n\n"
        "CAUSES OF ACTION:\n"
        "Count I: Breach of Contract - Failure to pay for services rendered\n"
        "Count II: Quantum Meruit - Unjust enrichment from services received\n"
        "Count III: Account Stated - Unpaid invoices deemed admitted\n\n"
        "RELIEF REQUESTED:\n"
        "Plaintiff requests judgment in the amount of $347,850, plus interest at 9% per annum "
        "from the date of each unpaid invoice, costs, and attorneys' fees.\n\n"
        "Respectfully submitted,\n"
        "Harvey Specter (Bar No. NY-45678)\n"
        "Pearson Specter Litt LLP"
    ))
    path = OUTPUT_DIR / "case_brief.pdf"
    pdf.output(str(path))
    print(f"Created: {path}")


def sample_3_notice_letter():
    """Notice letter with mixed formatting (simulated annotation)."""
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()

    pdf.set_font("Courier", size=11)
    pdf.cell(0, 8, "NOTICE OF DEFAULT AND TERMINATION", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(5)

    pdf.set_font("Courier", size=10)
    pdf.multi_cell(0, 5, (
        "Date: April 2, 2024\n"
        "To: Harvey Specter, Managing Partner\n"
        "    Pearson Specter Litt LLP\n"
        "    1250 Avenue of the Americas\n"
        "    New York, NY 10020\n\n"
        "From: James Callis, CEO\n"
        "    GlobalCorp Industries Inc.\n\n"
        "RE: Notice of Default under Service Agreement dated January 15, 2024\n\n"
        "Dear Mr. Specter,\n\n"
        "Pursuant to Section 4 of the Service Agreement, this letter serves as formal "
        "notice that GlobalCorp Industries Inc. hereby terminates the Agreement effective "
        "immediately.\n\n"
        "GROUNDS FOR TERMINATION:\n"
        "1. Failure to meet milestone deadlines set forth in the Statement of Work.\n"
        "2. Unauthorized disclosure of confidential information to third parties.\n"
        "3. Billing discrepancies in invoices dated February 15 and March 1, 2024.\n\n"
        "We demand that all client files and materials be returned within 10 business days.\n\n"
        "This notice is sent without prejudice to any rights or claims GlobalCorp may have.\n\n"
        "Sincerely,\n"
        "James Callis\n"
        "Chief Executive Officer\n"
        "GlobalCorp Industries Inc.\n\n"
        "cc: Legal Department, GlobalCorp Industries\n"
        "    Sarah Mitchell, Esq., External Counsel"
    ))
    pdf.ln(3)
    pdf.set_font("Courier", "I", 8)
    pdf.multi_cell(0, 4, (
        "[HANDWRITTEN ANNOTATION - top margin]\n"
        "Received Apr 3 2024 - please respond by Apr 10 - HS\n"
        "[HANDWRITTEN ANNOTATION - side margin]\n"
        "Call James re: confidentiality clause - he's bluffing about #2"
    ))
    path = OUTPUT_DIR / "notice_letter.pdf"
    pdf.output(str(path))
    print(f"Created: {path}")


def main():
    sample_1_contract_scan()
    sample_2_case_brief()
    sample_3_notice_letter()
    print(f"\nAll samples created in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
