from flask import Blueprint, render_template,request,redirect,url_for,current_app
import sqlite3,os
from werkzeug.utils import secure_filename
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


UPLOAD_FOLDER = 'static/images'

''' Functions to fetch data from products and categories table
These will be used by other functions'''

def get_categories():
    con = sqlite3.connect('database.db')
    cursor = con.cursor()
    cursor.execute("select * from categories")
    categories = cursor.fetchall()
    con.close()
    return categories

def get_products():
    con = sqlite3.connect('database.db')
    cursor = con.cursor()
    cursor.execute("select * from products")
    products = cursor.fetchall()
    con.close()
    return products



'''Renders admin dashboard'''
@admin_bp.route('/dashboard')
def admin_dashboard():
    categories = get_categories()
    products = get_products()
    return render_template('admin/admin_dashboard.html', categories=categories,products=products )

'''REdirects to page from where admin can manage categories'''
@admin_bp.route('/admin_manage_categories')
def admin_manage_categories():
    categories = get_categories()
    return render_template("admin/admin_manage_categories.html",categories=categories)

'''REdirects to page from where admin can manage products'''
@admin_bp.route('/admin_manage_products')
def admin_manage_products():
    categories = get_categories()
    products = get_products()
    return render_template('admin/admin_manage_products.html',categories=categories ,products=products )




''' To create a new category'''
@admin_bp.route('/admin_create_category', methods=['POST'])
def admin_create_category():
    if request.method == 'POST':
        
        category_name =  request.form['category_name']
        
        
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        cursor.execute("insert into categories(category_name) VALUES (?)", (category_name,) )
       
        conn.commit()
        conn.close()
        
        return redirect(url_for('admin.admin_dashboard') )
    
'''Logic to delete a category'''
@admin_bp.route('/admin_delete_category', methods=['POST'])
def admin_delete_category():
    if request.method ==  'POST':
        category_id =  request.form['category_id']
        
        con = sqlite3.connect('database.db')
        cursor = con.cursor()
        
        cursor.execute("DELETE FROM categories WHERE category_id=?", (category_id,))
        con.commit()
        con.close()
    
    return redirect(url_for('admin.admin_manage_categories'))




    
'''Logic to update a category''' 
@admin_bp.route('/admin_edit_category', methods=['POST'])
def admin_edit_category():
    if request.method == 'POST':
        category_id = request.form['category_id']
        new_category_name = request.form['new_category_name']
        
        if not new_category_name:
            return "New category name cannot be empty"
        
        con = sqlite3.connect('database.db')
        cursor = con.cursor()
        
        cursor.execute(
            "update categories SET category_name = ? WHERE category_id = ?",
            (new_category_name, category_id)
          )
        
        con.commit()
        con.close()
        
        return redirect(url_for('admin.admin_manage_categories'))
    
    
    
    
@admin_bp.route('/admin_create_product', methods=['POST'])
def admin_create_product():
    category_id = request.form['category_id']
    product_name = request.form['product_name']
    price = request.form['price']
    quantity= request.form['quantity']
    mfg_date = request.form['mfg_date']
    
    
    
    image = request.files['image']
    
    if image:
            filename = secure_filename(image.filename)
            
            image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename)) # took it fromn https://flask.palletsprojects.com/en/2.3.x/patterns/fileuploads/
            

    
    con = sqlite3.connect('database.db')
    cursor = con.cursor()
    
    cursor.execute('insert into products (category_id,product_name,price,quantity,mfg_date)  values(?,?,?,?,?)',
    (category_id,product_name,price,quantity,mfg_date ))
    
    con.commit()
    con.close()
    return redirect(url_for('admin.admin_dashboard'))
    
    
@admin_bp.route('/admin_delete_product', methods=['POST'])
def admin_delete_product():
   if request.method == 'POST':
      product_name = request.form['product_name']  
      con = sqlite3.connect('database.db')
      cursor = con.cursor()
    
      cursor.execute("delete from products where product_name=?",  (product_name,))
      con.commit()
      con.close()   
   return redirect(url_for('admin.admin_dashboard')) 






  
''' Editing a product, only the fields that we want i.e we can leave empty other input boxes
it uses 2 fuctions

The func   "update_product_in_database"  inside it updates the values
'''
@admin_bp.route('/admin_edit_product', methods=['POST'])
def admin_edit_product():
    if request.method == 'POST':
        product_id = request.form['product_id']
        new_product_name = request.form['product_name']
        new_quantity = request.form['quantity']
        new_price = request.form['price']
        new_mfg_date = request.form['mfg_date']
        
        # gets the existing product details from the database
        existing_product = query_database_to_get_product(product_id)
        
        
        image = request.files['image']
    
        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename)) # took it fromn https://flask.palletsprojects.com/en/2.3.x/patterns/fileuploads/
            
        
        if existing_product is None:
            return "Product not found"
        
        # Updates only the fields that are provided
        if new_product_name:
            existing_product['product_name'] = new_product_name
        if new_quantity:
            existing_product['quantity'] = new_quantity
        if new_price:
            existing_product['price'] = new_price
        if new_mfg_date:
            existing_product['mfg_date'] = new_mfg_date
        
        update_product_in_database(existing_product)
        
        return redirect(url_for('admin.admin_manage_products'))

    
    
#FUnction1 to update 
def update_product_in_database(product):
    con = sqlite3.connect('database.db')
    cursor = con.cursor()
    
    

    cursor.execute(
        '''
        update products
        set product_name = ?,
            quantity = ?,
            price = ?,
            mfg_date = ?
        where product_id = ?
        ''', (product['product_name'], 
              product['quantity'], 
              product['price'], 
              product['mfg_date'], 
              product['product_id'])
    )

    con.commit()
    con.close()
    
def query_database_to_get_product(product_id):
    con = sqlite3.connect('database.db')
    cursor = con.cursor()

    cursor.execute(
        ''' select * from products where product_id = ?
        ''',
        (product_id,)
    )

    product = cursor.fetchone()
    con.close()

    ''' It is a dictionary actually with key-value pairs'''
    if product:
        return {
            'product_id': product[0],
            'product_name': product[1],
            'category_id': product[2],
            'price': product[3],
            'quantity': product[4],
            'mfg_date': product[5]
        }
    else:
        return "product not found"
  

