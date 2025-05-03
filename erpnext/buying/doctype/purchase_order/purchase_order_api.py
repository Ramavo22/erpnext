import frappe

# Url for this API: /api/method/erpnext.buying.doctype.purchase_order.purchase_order_api.functionName

@frappe.whitelist(allow_guest=True)
def getListPurchaseOrderBySupplier(supplier: str):
    purchase_order = frappe.get_all(
        "Purchase Order",
        filters={"supplier": supplier},
        fields=["name", "supplier", "transaction_date","schedule_date",
                "total_qty","net_total","status"],
    )
    
    return {
        "message": "Purchase Order List loaded",
        "data": purchase_order
    }
    
    