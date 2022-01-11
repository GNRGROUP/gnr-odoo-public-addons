{
    'name': "stock_quant_editable_with_inventory_user",
    'summary': """ Allows inventory users to update stock quant and validate inventory adjustment """,
    'description': """
        Allows inventory users to update stock quant and validate inventory adjustment 
    """,
    'author': "G.N.R. GROUP CO.,LTD.",
    'website': "https://github.com/GNRGROUP/",
    'category': 'Inventory/Inventory',
    'version': '14.0.1.2.0',
    'depends': ['stock'],
    'application': False,
    'installable': True,
    'data': [
        'views/product.xml',
        'security/ir.model.access.csv'
    ]
}
