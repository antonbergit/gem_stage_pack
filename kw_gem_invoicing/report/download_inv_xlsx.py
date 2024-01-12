# pylint: disable=too-many-locals, too-many-statements
from odoo import models


class InvoiceXlsx(models.AbstractModel):
    _name = 'report.kw_gem_invoicing.kw_download_inv_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, invoices):
        for inv in invoices:
            report_name = inv.name

            bold_f14 = workbook.add_format()
            bold_f14.set_bold()
            bold_f14.set_font_size(14)

            border_1 = workbook.add_format({'border': 1})

            border_1_text_center = workbook.add_format()
            border_1_text_center.set_border(1)
            border_1_text_center.set_align('center')

            border_1_text_center_datetime = workbook.add_format()
            border_1_text_center_datetime.set_border(1)
            border_1_text_center_datetime.set_align('center')
            border_1_text_center_datetime.set_num_format('dd/mm/yy hh:mm')

            bold_bg_gray = workbook.add_format()
            bold_bg_gray.set_bold()
            bold_bg_gray.set_border(1)
            bold_bg_gray.set_bg_color('#D0cece')
            bold_bg_gray.set_align('center')

            bold_f14_align_center = workbook.add_format()
            bold_f14_align_center.set_bold()
            bold_f14_align_center.set_border(1)
            bold_f14_align_center.set_font_size(14)
            bold_f14_align_center.set_align('center')

            sheet = workbook.add_worksheet(report_name[:31])
            sheet.set_default_row(20)
            sheet.set_column('B:B', 16)
            sheet.set_column('C:D', 24)
            sheet.set_column('E:E', 20)
            sheet.set_column('F:F', 80)
            sheet.set_column('G:G', 15)

            sheet.write('B3', 'ინვოისის დეტალური ჩაშლა', bold_f14)
            sheet.write('B4', 'ინვოისის ნომერი:')
            sheet.write('C4', inv.name)
            narration_text = str(inv.narration).replace('</p><p>', ', ')[3: -4]
            sheet.write('B5', narration_text)
            sheet.write('B6', 'დამკვეთი:')
            sheet.write('C6', inv.partner_id.name)

            sheet.write('B9', 'ორდერის N', bold_bg_gray)
            sheet.write('C9', 'ორდერის თარიღი', bold_bg_gray)
            sheet.write('D9', 'პაციენტი', bold_bg_gray)
            sheet.write('E9', 'ს/კ', bold_bg_gray)
            sheet.write('F9', 'სერვისის დასახელება', bold_bg_gray)
            sheet.write('G9', 'თანხა', bold_bg_gray)

            start = 10
            lines = inv.invoice_line_ids
            case = inv.invoice_origin

            for i, line in enumerate(lines):
                order = inv.env['sale.order'].sudo().search(
                    [('name', '=', case)],
                    limit=1
                )
                if 'Additional Discount' in line.name:
                    continue
                if line.display_type == 'line_section':
                    case = line.name
                    start -= 1
                else:
                    sheet.write(
                        f'B{start + i}',
                        case,
                        border_1_text_center
                    )
                    sheet.write(
                        f'C{start + i}',
                        order.date_order,
                        border_1_text_center_datetime
                    )
                    sheet.write(
                        f'D{start + i}',
                        order.kw_patient_id.name,
                        border_1_text_center
                    )
                    sheet.write(
                        f'E{start + i}',
                        order.kw_patient_vat,
                        border_1_text_center
                    )
                    sheet.write(
                        f'F{start + i}',
                        line.name,
                        border_1
                    )
                    sheet.write(
                        f'G{start + i}',
                        line.price_total,
                        border_1_text_center
                    )
            sheet.write(
                f'G{start + len(lines) + 2}',
                inv.kw_total_payable_amount,
                bold_f14_align_center
            )
