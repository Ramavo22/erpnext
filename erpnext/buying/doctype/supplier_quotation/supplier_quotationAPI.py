import frappe


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
                    "rate": item.rate,
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

 #   apps/erpnext/erpnext.buying.doctype.supplier_quotation.supplier_quotationAPI