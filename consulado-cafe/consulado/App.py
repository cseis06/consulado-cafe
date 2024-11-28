# pip3 install flask flask-mysqldb
import base64
import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from flask_mysqldb import MySQL

# Creamos un objeto con el nombre app y le pasamos el parámetro name
app = Flask(__name__)

#Configuracion
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''  # Cambia 'password' por tu contraseña real
app.config['MYSQL_DB'] = 'cafe_consulado'  # Verifica el nombre de tu base de datos
app.config['MYSQL_SSL_CA'] = 'C:/xampp/mysql/certs/ca-cert.pem'
app.config['MYSQL_SSL_CERT'] = 'C:/xampp/mysql/certs/server-cert.pem'
app.config['MYSQL_SSL_KEY'] = 'C:/xampp/mysql/certs/server-key.pem'
mysql = MySQL(app)

#Clave
app.secret_key = 'mysecretkey'
#Creacion de bandera
bandera = False

#Inicio
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/')
def Index():
    return render_template('index.html')

#Boton Main
@app.route('/swicht_main')
def swicht_main():
    return render_template('index.html')

# Botón clientes
@app.route('/swicht_clientes')
def swicht_clientes():
    cur = mysql.connection.cursor()
    cur.execute(''' 
        SELECT idClientes, nombre, telefono, gmail, estado 
        FROM clientes 
        WHERE estado = TRUE
    ''')
    data = cur.fetchall()

    # Preparar los datos para la tabla
    clientes = []
    for row in data:
        # Incluye el ID como el primer elemento para facilitar operaciones
        clientes.append((row[0], row[1], row[2], row[3], row[4]))

    cliente_m = session.get('cliente_m')
    session.pop('cliente_m', None)

    return render_template('clientes.html', clientes=clientes, bandera=bandera, cliente_m=cliente_m)

#Botón empleados
@app.route('/swicht_empleados')
def swicht_empleados():
    cur = mysql.connection.cursor()
    cur.execute('''
        SELECT idEmpleados, nombre, apellido, numero, gmail, estado
        FROM empleados
        WHERE estado = TRUE
    ''')
    data = cur.fetchall()
    
    # Preparar los datos para la tabla
    empleados = []
    for row in data:
        # Incluye el ID como el primer elemento para facilitar operaciones
        empleados.append((row[0], row[1], row[2], row[3], row[4]))

    empleado_m = session.get('empleado_m')
    session.pop('empleado_m', None)

    return render_template('empleados.html', empleados=empleados, bandera=bandera, empleado_m=empleado_m)

#Boton Productos
@app.route('/swicht_productos')
def swicht_productos():
    cur = mysql.connection.cursor()
    cur.execute('''
        SELECT p.idProductos, p.nombre, p.precio, p.cantidad, p.imagen, p.estado, pr.nombre AS proveedor_nombre
        FROM productos p
        JOIN proveedores pr ON p.proveedores_idProveedor = pr.idProveedor
        WHERE p.estado = TRUE
    ''')
    data = cur.fetchall()
    # Codificar solo la imagen en base64
    productos = []
    for row in data:
        # Codificar la imagen en base64 si existe
        imagen_base64 = base64.b64encode(row[4]).decode('utf-8') if row[4] else None
        # Reemplazar la imagen binaria con su versión en base64 en el tuple
        productos.append((row[0], row[1], row[2], row[3], imagen_base64, row[5], row[6]))
    
    producto_m = session.get('producto_m')
    if producto_m is not None:
        cur.execute('SELECT imagen FROM productos WHERE idProductos = %s', (producto_m[0],))
        imagen_data = cur.fetchone()
        if imagen_data and imagen_data[0]:
            # Codificar la imagen recuperada en base64
            imagen_base64 = base64.b64encode(imagen_data[0]).decode('utf-8')
            producto_m = list(producto_m)  # Convertir a lista para modificar
            producto_m[4] = imagen_base64  # Actualizar el índice 4 con la imagen codificada

    session.pop('producto_m', None)

    return render_template('productos.html', productos = productos, bandera = bandera, producto_m = producto_m)

#Boton proveedores
@app.route('/swicht_proveedores')
def swicht_proveedores():
    cur = mysql.connection.cursor()
    cur.execute('''
        SELECT idProveedor, nombre, telefono, gmail, estado
        FROM proveedores
        WHERE estado = TRUE
    ''')
    data = cur.fetchall()
    
    # Preparar los datos para la tabla
    proveedores = []
    for row in data:
        # Incluye el ID como el primer elemento para facilitar operaciones
        proveedores.append((row[0], row[1], row[2], row[3]))

    proveedor_m = session.get('proveedor_m')
    session.pop('proveedor_m', None)

    return render_template('proveedores.html', proveedores=proveedores, bandera=bandera, proveedor_m=proveedor_m)
    
# Ruta para descargar el archivo PDF
@app.route('/menu')
def menu():
    # Ruta relativa al directorio 'pdfs'
    carpeta_pdfs = os.path.join(os.getcwd(), 'pdfs')
    nombre_pdf = 'Menú café consulado .pdf'
    
    # Verificar si el archivo existe
    if os.path.exists(os.path.join(carpeta_pdfs, nombre_pdf)):
        return send_from_directory(carpeta_pdfs, nombre_pdf, as_attachment=True)  # Enviar el archivo como adjunto
    else:
        return redirect(url_for('index'))  # Redirigir al inicio o a la página que desees

#Agregar productos
@app.route('/agg_productos', methods = ['POST'])
def agg_productos():
    global bandera

    if bandera:
        id_producto = session.get('idProducto')
        session.pop('idProducto', None)
        bandera = False

        nombre = request.form['nombre']
        precio = request.form['precio']
        cantidad = request.form['cantidad']
        proveedor = request.form['proveedor']

        # Validaciones básicas
        errores = []

        # Validar que no esté vacío
        if not nombre:
            errores.append("El nombre no puede estar vacío.")
        # Validar que el precio sea un número positivo
        try:
            precio_float = float(precio)
            if precio_float <= 0:
                errores.append("El precio debe ser un número positivo.")
        except ValueError:
            errores.append("El precio debe ser un número válido.")

        # Validar que la cantidad sea un número positivo
        try:
            cantidad_float = float(cantidad)
            if cantidad_float <= 0:
                errores.append("La cantidad debe ser un número positivo.")
        except ValueError:
            errores.append("La cantidad debe ser un número válido.")
        if not proveedor:
            errores.append("Debe seleccionar un proveedor.")

        # Validar que el nombre no sea solo números
        if nombre.isdigit():
            errores.append("El nombre no puede contener solo números.")

        # Validar si el proveedor existe en la base de datos
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) FROM proveedores WHERE nombre = %s", (proveedor,))
        proveedor_existe = cur.fetchone()[0]

        if not proveedor_existe:
            errores.append(f"El proveedor '{proveedor}' no existe en la base de datos.")

        # Si hay errores, devolverlos al usuario
        if errores:
            for error in errores:
                flash(error)
            return redirect(url_for('swicht_productos'))
        
        if 'imagen' in request.files and request.files['imagen']:

            imagen = request.files['imagen']
            imagen_binaria = imagen.read()

            cur = mysql.connection.cursor()
            cur.execute('''
                            UPDATE productos
                            SET nombre = %s, 
                                precio = %s, 
                                cantidad = %s, 
                                imagen = %s, 
                                proveedores_idProveedor = (SELECT idProveedor FROM proveedores WHERE nombre = %s)
                            WHERE idProductos = %s
                        ''', (nombre, precio, cantidad, imagen_binaria, proveedor, id_producto))
            mysql.connection.commit()


        else:

            cur = mysql.connection.cursor()
            cur.execute('''
                            UPDATE productos
                            SET nombre = %s, 
                                precio = %s, 
                                cantidad = %s, 
                                proveedores_idProveedor = (SELECT idProveedor FROM proveedores WHERE nombre = %s)
                            WHERE idProductos = %s
                        ''', (nombre, precio, cantidad, proveedor, id_producto))
            mysql.connection.commit()

        flash('Producto modificado satisfactoriamente')
        return redirect(url_for('swicht_productos'))

    else:

        if request.method == 'POST':

            nombre = request.form['nombre']
            precio = request.form['precio']
            cantidad = request.form['cantidad']
            proveedor = request.form['proveedor']

            # Validaciones básicas
            errores = []

            # Validar que el precio sea un número positivo
            try:
                precio_float = float(precio)
                if precio_float <= 0:
                    errores.append("El precio debe ser un número positivo.")
            except ValueError:
                errores.append("El precio debe ser un número válido.")

            # Validar que la cantidad sea un número positivo
            try:
                cantidad_float = float(cantidad)
                if cantidad_float <= 0:
                    errores.append("La cantidad debe ser un número positivo.")
            except ValueError:
                errores.append("La cantidad debe ser un número válido.")
            if not proveedor:
                errores.append("Debe seleccionar un proveedor.")

            # Validar que el nombre no sea solo números
            if nombre.isdigit():
                errores.append("El nombre no puede contener solo números.")

            # Validar si el proveedor existe en la base de datos
            cur = mysql.connection.cursor()
            cur.execute("SELECT COUNT(*) FROM proveedores WHERE nombre = %s and estado = True", (proveedor,))
            proveedor_existe = cur.fetchone()[0]

            if not proveedor_existe:
                errores.append(f"El proveedor '{proveedor}' no existe en la base de datos.")

            # Validar si el producto existe en la base de datos
            cur = mysql.connection.cursor()
            cur.execute("SELECT COUNT(*) FROM productos WHERE nombre = %s and estado = True", (nombre,))
            producto_existe = cur.fetchone()[0]

            if producto_existe > 0:
                errores.append(f"El producto '{nombre}' ya existe en la base de datos.")

            # Si hay errores, devolverlos al usuario
            if errores:
                for error in errores:
                    flash(error)
                return redirect(url_for('swicht_productos'))

            # Si quieres manejar una imagen
            if 'imagen' in request.files and request.files['imagen']:

                imagen = request.files['imagen']
                imagen_binaria = imagen.read()
                cur = mysql.connection.cursor()
                cur.execute('''
                                INSERT INTO productos (nombre, precio, cantidad, imagen, estado, proveedores_idProveedor)
                                VALUES (%s, %s, %s, %s, %s, (SELECT idProveedor FROM proveedores WHERE nombre = %s))
                            ''', (nombre, precio, cantidad, imagen_binaria, True, proveedor))
                mysql.connection.commit()

                flash('Producto añadido satisfactoriamente')

                return redirect(url_for('swicht_productos'))
            else:

                flash('No se ha subido ninguna imagen')

                return redirect(url_for('swicht_productos'))

#Eliminar productos
@app.route('/eliminar_productos/<id>')
def delete_productos(id):
    cur = mysql.connection.cursor()
    cur.execute('UPDATE productos SET estado = %s WHERE idProductos = %s', (False, id))
    mysql.connection.commit()

    flash('Producto removido correctamente')

    return redirect(url_for('swicht_productos'))

#Editar productos
@app.route('/editar_productos/<id>')
def editar_producto(id):
    cur = mysql.connection.cursor()
    cur.execute('''
        SELECT p.idProductos, p.nombre, p.precio, p.cantidad, p.imagen, p.estado, pr.nombre AS proveedor_nombre
        FROM productos p
        JOIN proveedores pr ON p.proveedores_idProveedor = pr.idProveedor
        WHERE p.idProductos = %s
    ''', (id))
    data = cur.fetchone()

    data = list(data)
    data[4] = None

    session['producto_m'] = data
    session['idProducto'] = data[0]

    global bandera
    bandera = True

    return redirect(url_for('swicht_productos'))

#Buscar productos
@app.route('/buscar_productos/', methods=['GET'])
def buscar_productos():
    global bandera

    # Obtener el término de búsqueda desde los parámetros de la URL
    query = request.args.get('query', '').strip()

    # Validar que no esté vacío
    if not query:
        flash("Por favor, ingresa un término de búsqueda.")
        return redirect(url_for('swicht_productos'))

    cur = mysql.connection.cursor()
    cur.execute('''  
        SELECT p.idProductos, p.nombre, p.precio, p.cantidad, p.imagen, p.proveedores_idProveedor, pr.nombre AS proveedor
        FROM productos p
        JOIN proveedores pr ON p.proveedores_idProveedor = pr.idProveedor
        WHERE p.nombre LIKE %s AND p.estado = True
    ''', (f"%{query}%",))  # Buscar productos cuyo nombre contenga el texto de búsqueda
    resultados = cur.fetchall()

    # Cambiar el formato para que sea accesible con los índices mencionados
    productos = []
    for row in resultados:
        # Codificar la imagen en base64 si existe
        if row[4]:  # Si la imagen no es nula
            imagen_base64 = base64.b64encode(row[4]).decode('utf-8')
        else:
            imagen_base64 = None

        productos.append([row[0], row[1], row[2], row[3], imagen_base64, row[5], row[6]])

    return render_template('productos.html', productos=productos, query=query, bandera=bandera)

#Agregar proveedores
@app.route('/agg_proveedores', methods=['POST'])
def agg_proveedores():
    global bandera

    if bandera:
        id_proveedor = session.get('idProveedor')
        session.pop('idProveedor', None)
        bandera = False

        nombre = request.form['nombre']
        telefono = request.form['telefono']
        gmail = request.form['gmail']

        # Validaciones básicas
        errores = []

        # Validar que el nombre no sea solo números
        if nombre.isdigit():
            errores.append("El nombre no puede contener solo números.")

        # Validar que el teléfono contenga solo números
        if telefono and not telefono.isdigit():
            errores.append("El teléfono debe contener solo números.")

        # Si hay errores, devolverlos al usuario
        if errores:
            for error in errores:
                flash(error)
            return redirect(url_for('swicht_proveedores'))

        # Actualizar proveedor si `bandera` está activada
        cur = mysql.connection.cursor()
        cur.execute('''
            UPDATE proveedores
            SET nombre = %s, telefono = %s, gmail = %s
            WHERE idProveedor = %s
        ''', (nombre, telefono, gmail, id_proveedor))
        mysql.connection.commit()

        flash('Proveedor modificado satisfactoriamente')
        return redirect(url_for('swicht_proveedores'))

    else:
        if request.method == 'POST':
            nombre = request.form['nombre']
            telefono = request.form['telefono']
            gmail = request.form['gmail']

            # Validaciones básicas
            errores = []

            # Validar que el nombre no sea solo números
            if nombre.isdigit():
                errores.append("El nombre no puede contener solo números.")

            # Validar que el teléfono contenga solo números
            if telefono and not telefono.isdigit():
                errores.append("El teléfono debe contener solo números.")

            # Validar si el proveedor ya existe en la base de datos
            cur = mysql.connection.cursor()
            cur.execute("SELECT COUNT(*) FROM proveedores WHERE nombre = %s", (nombre,))
            proveedor_existe = cur.fetchone()[0]

            if proveedor_existe > 0:
                errores.append(f"El proveedor '{nombre}' ya existe en la base de datos.")

            # Si hay errores, devolverlos al usuario
            if errores:
                for error in errores:
                    flash(error)
                return redirect(url_for('swicht_proveedores'))

            # Insertar proveedor
            cur = mysql.connection.cursor()
            cur.execute('''
                INSERT INTO proveedores (nombre, telefono, gmail, estado)
                VALUES (%s, %s, %s, %s)
            ''', (nombre, telefono, gmail, True))
            mysql.connection.commit()

            flash('Proveedor añadido satisfactoriamente')
            return redirect(url_for('swicht_proveedores'))

#Eliminar proveedores
@app.route('/eliminar_proveedores/<id>')
def delete_proveedores(id):
    cur = mysql.connection.cursor()
    cur.execute('UPDATE proveedores SET estado = %s WHERE idProveedor = %s', (False, id))
    mysql.connection.commit()

    flash('Proveedor removido correctamente')

    return redirect(url_for('swicht_proveedores'))

#Editar proveedores
@app.route('/editar_proveedores/<id>')
def editar_proveedor(id):
    cur = mysql.connection.cursor()
    cur.execute('''
        SELECT idProveedor, nombre, telefono, gmail, estado
        FROM proveedores
        WHERE idProveedor = %s
    ''', (id,))
    data = cur.fetchone()

    # Convertir los datos a una lista para poder modificarlos si es necesario
    data = list(data)
    data[4] = None  # Limpiar el campo 'estado' para no enviarlo a la plantilla

    session['proveedor_m'] = data
    session['idProveedor'] = data[0]  # Guardar el ID del proveedor en la sesión

    global bandera
    bandera = True

    return redirect(url_for('swicht_proveedores'))

#Buscar proveedores
@app.route('/buscar_proveedores/', methods=['GET'])
def buscar_proveedores():
    global bandera

    # Obtener el término de búsqueda desde los parámetros de la URL
    query = request.args.get('query', '').strip()

    # Validar que no esté vacío
    if not query:
        flash("Por favor, ingresa un término de búsqueda.")
        return redirect(url_for('swicht_proveedores'))

    cur = mysql.connection.cursor()
    cur.execute('''
        SELECT idProveedor, nombre, telefono, gmail, estado
        FROM proveedores
        WHERE nombre LIKE %s AND estado = True
    ''', (f"%{query}%",))  # Buscar proveedores cuyo nombre contenga el texto de búsqueda
    resultados = cur.fetchall()

    # Convertir los resultados a una lista de tuplas (formato simple)
    proveedores = [(row[0], row[1], row[2], row[3]) for row in resultados]

    return render_template('proveedores.html', proveedores=proveedores, query=query, bandera=bandera)

#Agregar empleados
@app.route('/agg_empleados', methods=['POST'])
def agg_empleados():
    global bandera

    if bandera:
        id_empleado = session.get('idEmpleado')
        session.pop('idEmpleado', None)
        bandera = False

        nombre = request.form['nombre']
        apellido = request.form['apellido']
        numero = request.form['numero']
        gmail = request.form['gmail']

        # Validaciones básicas
        errores = []

        # Validar que el nombre no sea solo números
        if nombre.isdigit():
            errores.append("El nombre no puede contener solo números.")
        
        # Validar que el apellido no sea solo números
        if apellido.isdigit():
            errores.append("El apellido no puede contener solo números.")

        # Validar que el número contenga solo números
        if numero and not numero.isdigit():
            errores.append("El número debe contener solo números.")

        # Si hay errores, devolverlos al usuario
        if errores:
            for error in errores:
                flash(error)
            return redirect(url_for('swicht_empleados'))

        # Actualizar empleado si `bandera` está activada
        cur = mysql.connection.cursor()
        cur.execute(''' 
            UPDATE empleados
            SET nombre = %s, apellido = %s, numero = %s, gmail = %s
            WHERE idEmpleados = %s
        ''', (nombre, apellido, numero, gmail, id_empleado))
        mysql.connection.commit()

        flash('Empleado modificado satisfactoriamente')
        return redirect(url_for('swicht_empleados'))

    else:
        if request.method == 'POST':
            nombre = request.form['nombre']
            apellido = request.form['apellido']
            numero = request.form['numero']
            gmail = request.form['gmail']

            # Validaciones básicas
            errores = []

            # Validar que el nombre no sea solo números
            if nombre.isdigit():
                errores.append("El nombre no puede contener solo números.")

            # Validar que el apellido no sea solo números
            if apellido.isdigit():
                errores.append("El apellido no puede contener solo números.")

            # Validar que el número contenga solo números
            if numero and not numero.isdigit():
                errores.append("El número debe contener solo números.")

            # Validar si el empleado ya existe en la base de datos
            cur = mysql.connection.cursor()
            cur.execute("SELECT COUNT(*) FROM empleados WHERE nombre = %s AND apellido = %s", (nombre, apellido))
            empleado_existe = cur.fetchone()[0]

            if empleado_existe > 0:
                errores.append(f"El empleado '{nombre} {apellido}' ya existe en la base de datos.")

            # Si hay errores, devolverlos al usuario
            if errores:
                for error in errores:
                    flash(error)
                return redirect(url_for('swicht_empleados'))

            # Insertar empleado
            cur = mysql.connection.cursor()
            cur.execute('''
                INSERT INTO empleados (nombre, apellido, numero, gmail, estado)
                VALUES (%s, %s, %s, %s, %s)
            ''', (nombre, apellido, numero, gmail, True))
            mysql.connection.commit()

            flash('Empleado añadido satisfactoriamente')
            return redirect(url_for('swicht_empleados'))

#Eliminar empleados
@app.route('/eliminar_empleados/<id>')
def delete_empleados(id):
    cur = mysql.connection.cursor()
    cur.execute('UPDATE empleados SET estado = %s WHERE idEmpleados = %s', (False, id))
    mysql.connection.commit()

    flash('Empleado removido correctamente')

    return redirect(url_for('swicht_empleados'))

#Editar empleados
@app.route('/editar_empleados/<id>')
def editar_empleado(id):
    cur = mysql.connection.cursor()
    cur.execute('''
        SELECT idEmpleados, nombre, apellido, numero, gmail, estado
        FROM empleados
        WHERE idEmpleados = %s
    ''', (id,))
    data = cur.fetchone()

    # Convertir los datos a una lista para poder modificarlos si es necesario
    data = list(data)
    data[5] = None  # Limpiar el campo 'estado' para no enviarlo a la plantilla

    session['empleado_m'] = data
    session['idEmpleado'] = data[0]  # Guardar el ID del empleado en la sesión

    global bandera
    bandera = True

    return redirect(url_for('swicht_empleados'))

#Buscar empleados
@app.route('/buscar_empleados/', methods=['GET'])
def buscar_empleados():
    global bandera

    # Obtener el término de búsqueda desde los parámetros de la URL
    query = request.args.get('query', '').strip()

    # Validar que no esté vacío
    if not query:
        flash("Por favor, ingresa un término de búsqueda.")
        return redirect(url_for('swicht_empleados'))

    cur = mysql.connection.cursor()
    cur.execute('''
        SELECT idEmpleados, nombre, apellido, numero, gmail, estado
        FROM empleados
        WHERE nombre LIKE %s AND estado = True
    ''', (f"%{query}%",))  # Buscar empleados cuyo nombre contenga el texto de búsqueda
    resultados = cur.fetchall()

    # Convertir los resultados a una lista de tuplas (formato simple)
    empleados = [(row[0], row[1], row[2], row[3], row[4]) for row in resultados]

    return render_template('empleados.html', empleados=empleados, query=query, bandera=bandera)

#Agregar clientes
@app.route('/agg_clientes', methods=['POST'])
def agg_clientes():
    global bandera

    if bandera:
        id_cliente = session.get('idCliente')
        session.pop('idCliente', None)
        bandera = False

        nombre = request.form['nombre']
        telefono = request.form['telefono']
        gmail = request.form['gmail']

        # Validaciones básicas
        errores = []

        # Validar que el nombre no sea solo números
        if nombre.isdigit():
            errores.append("El nombre no puede contener solo números.")
        
        # Validar que el teléfono contenga solo números
        if telefono and not telefono.isdigit():
            errores.append("El teléfono debe contener solo números.")

        # Si hay errores, devolverlos al usuario
        if errores:
            for error in errores:
                flash(error)
            return redirect(url_for('swicht_clientes'))

        # Actualizar cliente si `bandera` está activada
        cur = mysql.connection.cursor()
        cur.execute(''' 
            UPDATE clientes
            SET nombre = %s, telefono = %s, gmail = %s
            WHERE idClientes = %s
        ''', (nombre, telefono, gmail, id_cliente))
        mysql.connection.commit()

        flash('Cliente modificado satisfactoriamente')
        return redirect(url_for('swicht_clientes'))

    else:
        if request.method == 'POST':
            nombre = request.form['nombre']
            telefono = request.form['telefono']
            gmail = request.form['gmail']

            # Validaciones básicas
            errores = []

            # Validar que el nombre no sea solo números
            if nombre.isdigit():
                errores.append("El nombre no puede contener solo números.")

            # Validar que el teléfono contenga solo números
            if telefono and not telefono.isdigit():
                errores.append("El teléfono debe contener solo números.")

            # Validar si el cliente ya existe en la base de datos
            cur = mysql.connection.cursor()
            cur.execute("SELECT COUNT(*) FROM clientes WHERE nombre = %s", (nombre,))
            cliente_existe = cur.fetchone()[0]

            if cliente_existe > 0:
                errores.append(f"El cliente '{nombre}' ya existe en la base de datos.")

            # Si hay errores, devolverlos al usuario
            if errores:
                for error in errores:
                    flash(error)
                return redirect(url_for('swicht_clientes'))

            # Insertar cliente
            cur = mysql.connection.cursor()
            cur.execute(''' 
                INSERT INTO clientes (nombre, telefono, gmail, estado)
                VALUES (%s, %s, %s, %s)
            ''', (nombre, telefono, gmail, True))
            mysql.connection.commit()

            flash('Cliente añadido satisfactoriamente')
            return redirect(url_for('swicht_clientes'))

#Eliminar clientes
@app.route('/eliminar_clientes/<id>')
def delete_clientes(id):
    cur = mysql.connection.cursor()
    cur.execute('UPDATE clientes SET estado = %s WHERE idClientes = %s', (False, id))
    mysql.connection.commit()

    flash('Cliente removido correctamente')

    return redirect(url_for('swicht_clientes'))

#Editar clientes
@app.route('/editar_clientes/<id>')
def editar_cliente(id):
    cur = mysql.connection.cursor()
    cur.execute(''' 
        SELECT idClientes, nombre, telefono, gmail, estado 
        FROM clientes
        WHERE idClientes = %s
    ''', (id,))
    data = cur.fetchone()

    # Convertir los datos a una lista para poder modificarlos si es necesario
    data = list(data)
    data[4] = None  # Limpiar el campo 'estado' para no enviarlo a la plantilla

    session['cliente_m'] = data
    session['idCliente'] = data[0]  # Guardar el ID del cliente en la sesión

    global bandera
    bandera = True

    return redirect(url_for('swicht_clientes'))

#Buscar clientes
@app.route('/buscar_clientes/', methods=['GET'])
def buscar_clientes():
    global bandera

    # Obtener el término de búsqueda desde los parámetros de la URL
    query = request.args.get('query', '').strip()

    # Validar que no esté vacío
    if not query:
        flash("Por favor, ingresa un término de búsqueda.")
        return redirect(url_for('swicht_clientes'))

    cur = mysql.connection.cursor()
    cur.execute(''' 
        SELECT idClientes, nombre, telefono, gmail, estado
        FROM clientes
        WHERE nombre LIKE %s AND estado = True
    ''', (f"%{query}%",))  # Buscar clientes cuyo nombre contenga el texto de búsqueda
    resultados = cur.fetchall()

    # Convertir los resultados a una lista de tuplas (formato simple)
    clientes = [(row[0], row[1], row[2], row[3]) for row in resultados]

    return render_template('clientes.html', clientes=clientes, query=query, bandera=bandera)

#Reset Bandera
@app.route('/reset_bandera', methods=['POST'])
def reset_bandera():
    global bandera
    bandera = False
    return '', 204

if __name__ == '__main__':
    app.run(port=5000, debug=True)