from flask import Blueprint, render_template,request,redirect,url_for,session
import sqlite3


user_bp = Blueprint('user_bp', __name__, url_prefix='/')

def get_products():
    con = sqlite3.connect('database.db')
    cursor = con.cursor()
    cursor.execute("select  * FROM products")
    products = cursor.fetchall()
    con.close()
    
    return products

def get_categories():
    con = sqlite3.connect('database.db')
    cursor = con.cursor()
    cursor.execute(" select *  from categories")
    categories = cursor.fetchall()
    con.close()
    return categories

def get_category_name(category_id):
    con = sqlite3.connect('database.db')
    cursor = con.cursor()
    
    cursor.execute("select category_name from categories where category_id = ?", (category_id,))
    category_name = cursor.fetchone()[0]  # Fetches the first column of the result (category_name)
    
    con.close()
    
    return category_name
    

    

@user_bp.route('/user_home')
def user_home():
    products = get_products()
    categories=get_categories()
    latest_products = sorted(products,reverse=True)
    
    
    return render_template('/user_home/user_home.html', products=products,categories=categories,get_category_name=get_category_name, latest_products=latest_products)



@user_bp.route('/out_of_stock')
def out_of_stock():
    return render_template('/messages/outofstock.html')

@user_bp.route('/thank_you')
def  thank_you():
    return render_template('/messages/thanks.html')





def get_cart():
    con = sqlite3.connect('database.db')
    cursor = con.cursor()
    username = get_user_id_from_session()    
    cursor.execute("select * from  cart where username=?",(username,))
    cart = cursor.fetchall()
    con.close()
    
    return cart

@user_bp.route('/user_cart')
def user_cart():
    cart=get_cart()
    
    return render_template('/user_home/user_cart.html',cart=cart)


    

@user_bp.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    product_id = int(request.form['product_id'])
    quantity = int(request.form['quantity'])
    username = get_user_id_from_session()
    price = int(request.form['price'])
    product_name = request.form['product_name']

    if username is None:
        # Redirects to login if user is not logged in
        return redirect(url_for('auth_bp.login'))

    con = sqlite3.connect('database.db')
    cursor = con.cursor()

    cursor.execute("SELECT * FROM cart WHERE username = ? AND product_id = ?", (username, product_id))
    cart_row = cursor.fetchone()

    if cart_row:
        cart_id = cart_row[0]
        new_quantity = cart_row[3] + quantity  
        cursor.execute("update cart set quantity = ?, price = ? WHERE cart_id = ?", (new_quantity, price, cart_id))
    else:
        
        cursor.execute("insert into cart (username, product_id, quantity, price, product_name) VALUES (?, ?, ?, ?, ?)",
                       (username, product_id, quantity, price, product_name))
    con.commit()
    con.close()

    return redirect(url_for('user_bp.user_home'))


def get_user_id_from_session():
      return session.get('username')
  



#Toughesr part in the code
#first it fetches all cart items from current user
#Then checks if quantity is available in products table or not
# Then gives suitable errors if there is a problem
#If no error then updates quantity in products table
#then creates a new order in user-ORDERS table
#At the end cart item is deleted
#and user gets Thank you message

@user_bp.route('/buy_now', methods=['POST'])
def buy_now():
    con = sqlite3.connect('database.db')
    cursor = con.cursor()    
    username = get_user_id_from_session()
    cursor.execute("SELECT product_id, quantity FROM cart WHERE username = ?", (username,))
    cart_data = cursor.fetchall()
    
    
    
    for product_id, cart_quantity in cart_data:
          cursor.execute("select  quantity, price, product_name from   products where product_id = ?", (product_id,))
          product_data = cursor.fetchone()
          product_quantity, price, product_name = product_data
          
          if product_quantity == 0:
                con.close()
                return redirect(url_for('user_bp.out_of_stock'))
            
            
          if (cart_quantity > product_quantity):
            con.close()
            return "Error: You are trying to buy more than available quantity."
    
        
          else:
            new_quantity = product_quantity - cart_quantity
          
        
            cursor.execute("insert into user_orders (username, product_id, quantity, price, product_name) values(?, ?, ?, ?,?)",
            (username, product_id, cart_quantity,price, product_name))
          
            cursor.execute("update products set quantity = ? WHERE product_id = ?", (new_quantity, product_id))
          
            cursor.execute("delete from cart where username = ?", (username,))
            con.commit()
            con.close()
            return redirect(url_for('user_bp.thank_you'))





#deleting an item from cart giving providing cart id
@user_bp.route('/remove_from_cart/<int:cart_id>', methods=['POST'])
def remove_from_cart(cart_id):
    con = sqlite3.connect('database.db')
    cursor = con.cursor()
    username = get_user_id_from_session()
    
    cursor.execute("delete from cart where username = ? AND cart_id = ?", (username, cart_id))
    
    con.commit()
    con.close()
    
    return redirect(url_for('user_bp.user_cart'))






def get_orders():
    con = sqlite3.connect('database.db')
    cursor = con.cursor()
    username = get_user_id_from_session()    
    cursor.execute("select * from user_orders where username=?",(username,))
    orders = cursor.fetchall()
    con.close()
    
    return orders

@user_bp.route('/user_orders')
def user_orders():
    orders=get_orders()
    
    return render_template('/user_home/user_orders.html',orders=orders)

#categories and products table is joined on category_id so that we can fetch category name too
#this function searches required data  

def perform_search(query):
    con = sqlite3.connect('database.db')
    cursor = con.cursor()
    
    
    cursor.execute("""
        select p.*, c.category_name from products as p
        join categories as c ON p.category_id = c.category_id
        WHERE p.product_name like ? OR p.price like ? OR c.category_name like ?
    """, ('%' + query + '%', '%' + query + '%', '%' + query + '%'))
    
    results = cursor.fetchall()
    con.close()
    
    return results

@user_bp.route('/search_results', methods=['GET'])
def search_results():
    query = request.args.get('query')
    
    # Performing a search 
    results = perform_search(query)
    products = get_products()
    categories=get_categories()

    
    
    return render_template('/user_home/search_results.html', results=results, query=query,get_category_name=get_category_name)



    
    
