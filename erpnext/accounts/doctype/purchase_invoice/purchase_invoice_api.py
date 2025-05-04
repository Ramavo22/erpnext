import frappe

# Url for this API: /api/method/erpnext.accounts.doctype.purchase_invoice.purchase_invoice_api.getListPurchaseInvoice

@frappe.whitelist(allow_guest=True)
def getListPurchaseInvoice():
    purchase_invoices = frappe.get_all(
        "Purchase Invoice",
        fields=["name","supplier","due_date",
                "total_qty","total","net_total","status"],
        order_by="due_date desc"
    )
    
    return {
        "message": "Purchase Invoice List loaded",
        "data": purchase_invoices
    }
    

@frappe.whitelist(allow_guest=False)
def getListPurchaseInvoiceByName(name: str):
    try:
        purchase_invoice = frappe.get_doc("Purchase Invoice", name)
        data = {
            "name": purchase_invoice.name,
            "supplier": purchase_invoice.supplier,
            "due_date": purchase_invoice.due_date,
            "total_qty": purchase_invoice.total_qty,
            "total": purchase_invoice.total,
            "net_total": purchase_invoice.net_total,
            "status": purchase_invoice.status
        }
        return {
            "message": "Purchase Invoice loaded",
            "data": data
        }
    except frappe.DoesNotExistError:
        frappe.throw(f"Purchase Invoice {name} not found")