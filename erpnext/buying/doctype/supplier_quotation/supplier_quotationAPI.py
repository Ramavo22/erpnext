import frappe
import json



# get all supplier quotation list by supplier
@frappe.whitelist(allow_guest=True)
def getListSupplierQuotationBySupplier(supplier: str):
    supplier_quotation = frappe.get_all(
        "Supplier Quotation",
        filters={"supplier": supplier},
        fields=["name", "supplier", "transaction_date",
                "total_qty",
                "total","net_total","status","valid_till"],
        order_by="transaction_date desc"
    )
    
    return {
        "message": "Supplier Quotation List loaded",
        "data": supplier_quotation
    }
    
    
@frappe.whitelist(allow_guest=True)
def getAllDetailSupplierQuotation(quotation: str):
    try:
        doc = frappe.get_doc("Supplier Quotation", quotation)

        # Tu choisis uniquement les champs à exposer
        data = {
            "name": doc.name,
            "supplier": doc.supplier,
            "transaction_date": doc.transaction_date,
            "total_qty": doc.total_qty,
            "total": doc.total,
            "net_total": doc.net_total,
            "status": doc.status,
            "valid_till": doc.valid_till,
            "items": [
                {
                    "name": item.name,
                    "item_code": item.item_code,
                    "item_name": item.item_name,
                    "qty": item.qty,
                    "uom": item.uom,
                    "conversion_factor":item.conversion_factor,
                    "rate": item.rate,
                    "base_rate":item.base_rate,
                    "base_amount":item.base_amount,
                    "amount": item.amount
                }
                for item in doc.items
            ]
        }

        return {
            "message": "Supplier Quotation with items loaded",
            "data": data
        }

    except frappe.DoesNotExistError:
        return {
            "message": "Supplier Quotation not found",
            "data": None
        }
        
@frappe.whitelist(allow_guest=False)
def update_rate():
    try:
        # Lire le body brut JSON
        data = json.loads(frappe.request.get_data(as_text=True))

        item_name = data.get("item_name")
        new_rate = data.get("new_rate")

        if not item_name or new_rate is None:
            return {"status": "error", "message": "item_name and new_rate are required"}

        # Récupérer l’item et son parent
        item_doc = frappe.get_doc("Supplier Quotation Item", item_name)
        parent_doc = frappe.get_doc("Supplier Quotation", item_doc.parent)

        # Bypass validation
        parent_doc.flags.ignore_validate_update_after_submit = True
        parent_doc.flags.ignore_validate = True
        parent_doc.flags.ignore_permissions = True

        # Modifier le rate
        for item in parent_doc.items:
            if item.name == item_name:
                item.rate = float(new_rate)
                break

        parent_doc.calculate_taxes_and_totals()
        # Sauvegarder
        parent_doc.save()

        return {"status": "success", "message": "Rate updated"}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "update_rate_from_body failed")
        return {"status": "error", "message": str(e)}

 #   apps/erpnext/erpnext.buying.doctype.supplier_quotation.supplier_quotationAPI