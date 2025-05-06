import csv
import os
import frappe
from frappe import _

from collections import defaultdict
from datetime import datetime


@frappe.whitelist()
def import_data(file_url_supplier=None, file_url_material_request=None, file_url_quotation=None):
    try:
        if not file_url_supplier or not file_url_material_request or not file_url_quotation:
            frappe.throw(_("Tous les fichiers CSV doivent être fournis."))

        file_path_supplier = frappe.get_site_path('private', 'files', os.path.basename(file_url_supplier))
        file_path_material_request = frappe.get_site_path('private', 'files', os.path.basename(file_url_material_request))
        file_path_quotation = frappe.get_site_path('private', 'files', os.path.basename(file_url_quotation))

        # Vérifier si le fichier existe
        if not os.path.exists(file_path_supplier):
            frappe.throw(_("Le fichier n'existe pas : ") + file_path_supplier)
        if not os.path.exists(file_path_material_request):
            frappe.throw(_("Le fichier n'existe pas : ") + file_path_material_request)
        if not os.path.exists(file_path_quotation):
            frappe.throw(_("Le fichier n'existe pas : ") + file_path_quotation)

        # Importer les données
        supplier_import(file_path_supplier)
        material_request_import(file_path_material_request)
        quotation_import(file_path_quotation)

        # Nettoyage
        for file_path, file_url in zip(
            [file_path_supplier, file_path_material_request, file_path_quotation],
            [file_url_supplier, file_url_material_request, file_url_quotation]
        ):
            if os.path.exists(file_path):
                os.remove(file_path)
                frappe.logger().info(f"File deleted: {file_path}")

            file_doc = frappe.get_all("File", filters={"file_url": file_url}, fields=["name"])
            if file_doc:
                frappe.delete_doc("File", file_doc[0].name)
                frappe.logger().info(f"File document deleted: {file_url}")

        return "Lecture terminée avec succès"

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(message=str(e), title="Import CSV Error")
        frappe.throw(_("Une erreur est survenue pendant l'import : ") + str(e))


def supplier_import(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        data = []
        country_list = set()
        for i,row in enumerate(reader):
            
            country_list.add(row["country"])
            data.append(
                {
                    "supplier_name": row["supplier_name"],
                    "country": row["country"],
                    "supplier_type": row["type"],
                }
            )
            
        for i,row in enumerate(country_list):
            if not frappe.db.exists("Country", row):
                country_code = first_two_letter_upper_case(row)
                print(f"Country {row} with code {country_code} will be inserted")
                
                country = frappe.get_doc({
                    "doctype": "Country",
                    "country_name": row,
                    "code": country_code
                })
                
                country.insert()
                print(f"Country {row} inserted")
                
        frappe.db.commit()
        
        for i,row in enumerate(data):
            supplier = frappe.get_doc({
                "doctype": "Supplier",
                "supplier_name": row["supplier_name"],
                "country": row["country"],
                "supplier_type": row["supplier_type"],
            })
            supplier.insert()  
            print(f"Supplier {row['supplier_name']} inserted")  
        frappe.db.commit()
        
    print("Supplier import done")

def material_request_import(file_path):
    # step 0 = prepare the data
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        item_group_list = set()
        item_list = []
        warehouse_list = set()
        data = []
        
        
        for row in reader:
            item_group_list.add(row["item_groupe"])
            # Vérifie si le couple (item_name, item_group) existe déjà
            if (row["item_name"], row["item_groupe"]) not in [
                (item["item_name"], item["item_group"]) for item in item_list
            ]:
                item_code = frappe.model.naming.make_autoname('ITEM-.#####')
                item_list.append({
                    "item_code": item_code,
                    "item_name": row["item_name"],
                    "item_group": row["item_groupe"]
                })
            warehouse_list.add(row["target_warehouse"])
            data.append({
                "date": row["date"],
                "item_name": row["item_name"],
                "item_group": row["item_groupe"],
                "required_by": row["required_by"],
                "quantity": row["quantity"],
                "purpose": row["purpose"],
                "target_warehouse": row["target_warehouse"],
                "ref": row["ref"],
            })
            
    # step 1 = create the item groups
    for row in item_group_list:
        item_group = frappe.get_doc({
            "doctype": "Item Group",
            "item_group_name": row,
            "parent_item_group": "All Item Groups"
        })
        item_group.insert()
        print(f"Item group {row} inserted")
    frappe.db.commit()
    
    
    # step 1.1 = create the warehouse
    for row in warehouse_list:
        warehouse = frappe.get_doc({
            "doctype": "Warehouse",
            "name": row,
            "warehouse_name": row,
            "company": "Fanah's ERP",
            "is_group": 0,
        })
        warehouse.insert()
        print(f"Warehouse {row} inserted")
        
    frappe.db.commit()

    # step 2 = create the item
    for row in item_list:
        item = frappe.get_doc({
            "doctype": "Item",
            "item_code": row["item_code"],
            "item_name": row["item_name"],
            "item_group": row["item_group"],
            "stock_uom": "Unit",
        })
        item.insert()
        print(f"Item {row['item_name']} inserted")
        
    frappe.db.commit()
    # step 3 = create the material request
    grouped_data = defaultdict(list)

    for row in data:
        grouped_data[row["ref"]].append(row)

    for ref, rows in grouped_data.items():
        mr_doc = frappe.get_doc({
            "doctype": "Material Request",
            "custom_ref": ref,
            "transaction_date": dateToIsoDate(rows[0]["date"]),
            "company": "Fanah's ERP",
            "material_request_type": rows[0]["purpose"],
            "docstatus": 1,
            "items": []
        })
        for row in rows:
            item_code = frappe.get_value("Item", {"item_name": row["item_name"]}, "name")
            mr_doc.append("items",{
                "item_code": item_code,
                "item_name": row["item_name"],
                "item_group": row["item_group"],
                "schedule_date": dateToIsoDate(row["required_by"]),
                "qty": float(row["quantity"]),
                "uom": "Unit",
                "warehouse": warehouse_name(row["target_warehouse"]),
            })
        mr_doc.insert()
        print(f"Material Request {ref} inserted")
    frappe.db.commit()
    print("Material Request import done")



from erpnext.stock.doctype.material_request.material_request import make_request_for_quotation
def quotation_import(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        data = []
        for row in reader:
            data.append({
                "ref": row["ref_request_quotation"],
                "supplier": row["supplier"]
            })
            
        grouped_data = defaultdict(list)

        for row in data:
            grouped_data[row["ref"]].append(row)
            
        for ref, rows in grouped_data.items():
            mr_doc_name = frappe.get_value("Material Request", {"custom_ref": ref}, "name")
            if not mr_doc_name:
                frappe.throw(_("Material Request not found for ref: ") + ref)
            
            print(f"Material Request {mr_doc_name} found for ref: {ref}")
            
            rfq = make_request_for_quotation(mr_doc_name)
            
            print(f"RFQ {rfq} created for Material Request {mr_doc_name}")
            
            for row in rows:
                rfq.append("suppliers", {
                    "supplier": row["supplier"]
                })
                
            rfq.message_for_supplier= "Please provide your best price and delivery time."
            rfq.custom_ref = ref
            rfq.insert()
            rfq.submit()
            
        frappe.db.commit()   
        generate_supplier_quotation(grouped_data)

        print("Quotation import done")
        
from erpnext.buying.doctype.request_for_quotation.request_for_quotation import make_supplier_quotation_from_rfq
def generate_supplier_quotation(rfq_data):
    for ref, rows in rfq_data.items():
        rfq_name = frappe.get_value("Request for Quotation", {"custom_ref": ref}, "name")
        if not rfq_name:
            frappe.throw(_("Request for Quotation not found for ref: ") + ref)

        for row in rows:
            
            sq = make_supplier_quotation_from_rfq(rfq_name,for_supplier=row["supplier"])
            sq.insert()
        
    
    frappe.db.commit()
                   
    
@frappe.whitelist()
def reinit_base():
    
    doctype_list=[
        "Article",
        "Item",
        "Supplier",
        "Supplier Item",
        "Material Request",
        "Material Request Item",
        "Request for Quotation",
        "Request for Quotation Item",
        "Supplier Quotation",
        "Supplier Quotation Item",
        "Purchase Order",
        "Purchase Order Item",
        "Purchase Invoice",
        "Purchase Invoice Item",
        "Purchase Receipt",
        "Purchase Receipt Item",
        "Payment Request",
        "Payment Entry",
        "Bin",
        "Stock Ledger Entry",
        "Warehouse",
    ]
    
    
    
    for doctype in doctype_list:
        frappe.db.sql(f"TRUNCATE TABLE `tab{doctype}`")
        
    #Supprimer tous les Item Group sauf "All Item Groups"
    frappe.db.sql("""
        DELETE FROM `tabItem Group`
        WHERE name != 'All Item Groups'
    """)
    
    return "Reinit done"
            


###########################
# inner fonctions

def dateToIsoDate(datestr: str) -> str:
    """
    Convertit une date de format 'DD/MM/YYYY' en format ISO 'YYYY-MM-DD'.
    """
    try:
        return datetime.strptime(datestr, "%d/%m/%Y").date().isoformat()
    except ValueError:
        raise ValueError(f"Date invalide : '{datestr}' (attendu: JJ/MM/AAAA)")
    
    
def first_two_letter_upper_case(texte):
    
    if len(texte) <= 2:
        return texte.upper()
    return texte[:2].upper()

def warehouse_name(warehouse):
    """
    Renvoie le nom du warehouse
    exemple : "All Warehouse - FE for All Warehouse"
    """
    return warehouse+" - FE"
    

