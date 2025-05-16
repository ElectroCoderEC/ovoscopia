import mysql.connector


class Database:
    def __init__(self):

        db_config = {
            "user": "root",
            "password": "",
            "host": "localhost",
            "database": "pies",
        }

        self.config = db_config
        self.connection = None

    def connect(self):
        if self.connection is None:
            # self.connection = mysql.connector.connect(**self.config)
            self.connection = mysql.connector.connect(**self.config)

    def close(self):
        if self.connection is not None and self.connection.is_connected():
            self.connection.close()
            self.connection = None

    def insert_user(
        self, nombre, cedula, telefono, estatura, edad, peso, genero, imagen
    ):
        self.connect()
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO usuarios (nombre,cedula,telefono,estatura,edad,peso,genero,imagen) VALUES (%s, %s, %s, %s, %s, %s, %s,%s)",
            (nombre, cedula, telefono, estatura, edad, peso, genero, imagen),
        )
        self.connection.commit()
        cursor.close()
        # self.connection.close()

    def insert_pie(self, nombre, descripcion):
        self.connect()
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO plantillas (nombre,descripcion) VALUES (%s, %s)",
            (nombre, descripcion),
        )
        self.connection.commit()
        cursor.close()
        # self.connection.close()

    def insert_prueba(
        self,
        id_usuario,
        x_izquierdo,
        y_izquierdo,
        porcentaje_izquierda,
        id_plantilla_izquierda,
        x_derecha,
        y_derecha,
        porcentaje_derecha,
        id_plantilla_derecha,
        foto,
    ):
        self.connect()
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO pruebas (id_usuario, x_izquierdo, y_izquierdo, porcentaje_izquierda, id_plantilla_izquierda, x_derecha, y_derecha, porcentaje_derecha, id_plantilla_derecha, foto) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (
                id_usuario,
                x_izquierdo,
                y_izquierdo,
                porcentaje_izquierda,
                id_plantilla_izquierda,
                x_derecha,
                y_derecha,
                porcentaje_derecha,
                id_plantilla_derecha,
                foto,
            ),
        )
        self.connection.commit()
        cursor.close()
        # self.connection.close()

    def fetch_users(self):
        self.connect()
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM usuarios order by id DESC")
        users = cursor.fetchall()
        cursor.close()
        # self.connection.close()
        return users

    def fetch_plantillas(self):
        self.connect()
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM plantillas order by id ASC")
        plantillas = cursor.fetchall()
        cursor.close()
        # self.connection.close()
        return plantillas

    def fetch_configuraciones(self):
        self.connect()
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM configuraciones")
        plantillas = cursor.fetchall()
        cursor.close()
        return plantillas

    def fetch_test(self, idUsuario):
        self.connect()
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM pruebas WHERE id_usuario = %s", (idUsuario,))
        pruebas = cursor.fetchall()
        cursor.close()
        # self.connection.close()
        return pruebas

    def get_user_data(self, id_cliente):
        self.connect()
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE id = %s", (id_cliente,))
        user = cursor.fetchone()
        cursor.close()
        # self.connection.close()
        return user

    def get_user_cedula(self, id_cliente):
        self.connect()
        cursor = self.connection.cursor()
        cursor.execute("SELECT cedula FROM usuarios WHERE id = %s", (id_cliente,))
        user = cursor.fetchone()
        cursor.close()
        # self.connection.close()
        if user:
            return user[0]  # Return the cedula as a string

    def delete_user(self, id_cliente):
        self.connect()
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id = %s", (id_cliente,))
        self.connection.commit()
        cursor.close()
        # self.connection.close()

    def delete_pie(self, id_pie):
        self.connect()
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM plantillas WHERE id = %s", (id_pie,))
        self.connection.commit()
        cursor.close()
        # self.connection.close()

    def get_number_users(self):
        self.connect()
        cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(id) FROM usuarios")
        count = cursor.fetchone()
        cursor.close()
        # self.connection.close()
        return count[0]

    def get_number_plantillas(self):
        self.connect()
        cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(id) FROM plantillas")
        count = cursor.fetchone()
        cursor.close()
        # self.connection.close()
        return count[0]

    def get_number_tests(self):
        self.connect()
        cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(id) FROM pruebas")
        count = cursor.fetchone()
        cursor.close()
        # self.connection.close()
        return count[0]

    def update_plantilla(self, id, nombre, descripcion):
        self.connect()
        cursor = self.connection.cursor()
        cursor.execute(
            "UPDATE plantillas SET nombre = %s,descripcion = %s  WHERE id = %s",
            (
                nombre,
                descripcion,
                id,
            ),
        )
        self.connection.commit()
        cursor.close()

    def get_plantilla(self, id_plantilla):
        self.connect()
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM plantillas WHERE id = %s", (id_plantilla,))
        user = cursor.fetchone()
        cursor.close()
        # self.connection.close()
        return user

    def update_hsv(
        self,
        lower_h,
        lower_s,
        lower_v,
        upper_h,
        upper_s,
        upper_v,
        lower_h2,
        lower_s2,
        lower_v2,
        upper_h2,
        upper_s2,
        upper_v2,
    ):
        self.connect()
        cursor = self.connection.cursor()
        cursor.execute(
            "UPDATE configuraciones SET lowerH = %s,lowerS = %s,lowerV = %s,upperH = %s,upperS = %s,upperV = %s,lowerHdedos = %s,lowerSdedos = %s,lowerVdedos = %s,upperHdedos = %s,upperSdedos = %s,upperVdedos = %s  WHERE id = %s",
            (
                lower_h,
                lower_s,
                lower_v,
                upper_h,
                upper_s,
                upper_v,
                lower_h2,
                lower_s2,
                lower_v2,
                upper_h2,
                upper_s2,
                upper_v2,
                "1",
            ),
        )
        self.connection.commit()
        cursor.close()
        # self.connection.close()
