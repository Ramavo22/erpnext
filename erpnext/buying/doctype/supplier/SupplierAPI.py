import frappe


@frappe.whitelist(allow_guest=True)
def getListSupplier():
    supplier = frappe.get_all(
        "Supplier",
        fields=["name","supplier_name","supplier_type","country"]
    )
    
    return {
        "message": "Supplier List loaded",
        "data": supplier
    }
    
    #apps/erpnext/erpnext/buying/doctype/supplier/SupplierAPI.py