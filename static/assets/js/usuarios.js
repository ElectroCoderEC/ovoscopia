

/*=============================================
SUBIENDO LA FOTO DEL USUARIO
=============================================*/
$("#nuevaFoto").change(function () {

	var imagen = this.files[0];
	console.log(imagen)
	/*=============================================
		VALIDAMOS EL FORMATO DE LA IMAGEN SEA JPG O PNG
		=============================================*/

	if (imagen["type"] != "image/jpeg" && imagen["type"] != "image/png") {

		$(".nuevaFoto").val("");
		$('#modalAgregarUsuario').modal('hide'); // Cierra el modal


		Swal.fire({
			title: "Error al subir la imagen",
			text: "¡La imagen debe estar en formato JPG o PNG!",
			type: "error",
			confirmButtonText: "¡Cerrar!"
		});

	} else if (imagen["size"] > 2000000) {
		$('#modalAgregarUsuario').modal('hide'); // Cierra el modal


		$(".nuevaFoto").val("");

		Swal.fire({
			title: "Error al subir la imagen",
			text: "¡La imagen no debe pesar más de 2MB!",
			type: "error",
			confirmButtonText: "¡Cerrar!"
		});

	} else {

		var datosImagen = new FileReader;
		datosImagen.readAsDataURL(imagen);




		$(datosImagen).on("load", function (event) {

			var rutaImagen = event.target.result;


			$(".previsualizar").attr("src", rutaImagen);



		})

	}
})



$(".previsualizar").change(function () {

	var url = $(this).attr("src");
	console.log('URL de la imagen del elemento img:', url);


})

/*=============================================
EDITAR USUARIO
=============================================*/
$(".tablas").on("click", ".btnEditarUsuario", function () {

	var idUsuario = $(this).attr("idUsuario");

	var datos = new FormData();
	datos.append("idUsuario", idUsuario);

	$.ajax({

		url: "ajax/usuarios.ajax.php",
		method: "POST",
		data: datos,
		cache: false,
		contentType: false,
		processData: false,
		dataType: "json",
		success: function (respuesta) {

			$("#editarNombre").val(respuesta["nombre"]);
			$("#editarUsuario").val(respuesta["usuario"]);
			$("#editarPerfil").html(respuesta["perfil"]);
			$("#editarPerfil").val(respuesta["perfil"]);
			$("#fotoActual").val(respuesta["foto"]);

			$("#passwordActual").val(respuesta["password"]);

			if (respuesta["foto"] != "") {

				$(".previsualizarEditar").attr("src", respuesta["foto"]);

			} else {

				$(".previsualizarEditar").attr("src", "vistas/img/usuarios/default/anonymous.png");

			}

		}

	});

})



/*=============================================
REVISAR SI EL USUARIO YA ESTÁ REGISTRADO
=============================================*/

$("#nuevoUsuario").change(function () {

	$(".alert").remove();

	var usuario = $(this).val();

	var datos = new FormData();
	datos.append("validarUsuario", usuario);

	$.ajax({
		url: "ajax/usuarios.ajax.php",
		method: "POST",
		data: datos,
		cache: false,
		contentType: false,
		processData: false,
		dataType: "json",
		success: function (respuesta) {

			if (respuesta) {

				$("#nuevoUsuario").parent().after('<div class="alert alert-warning">Este usuario ya existe en la base de datos</div>');
				$("#nuevoUsuario").val("");

			}

		}

	})
})



/*=============================================
SELECCIONAR USUARIO
=============================================*/
$(".tablas").on("click", ".btnElegirUsuario", function () {

	var idUsuario = $(this).attr("idUsuario");

	Swal.fire({
		title: '¿Desea iniciar la prueba con este usuario?',
		text: "¡Si no lo está puede cancelar la accíón!",
		type: 'warning',
		showCancelButton: true,
		confirmButtonColor: '#3085d6',
		cancelButtonColor: '#d33',
		cancelButtonText: 'Cancelar',
		confirmButtonText: 'OK'
	}).then(function (result) {

		if (result.value) {


			$.ajax({
				url: '/select_user',
				type: 'POST',
				contentType: 'application/json',
				data: JSON.stringify({ idUsuario: idUsuario }),
				success: function (response) {
					if (response.redirect) {
						window.location.href = response.redirect + "?usuario=" + JSON.stringify(response.usuario);  //esto es con GET
						//window.location.href = response.usuario;
					} else {
						console.log("Error: Redirección no especificada.");
					}
				}
			});
		}
	})
})


/*=============================================
ELIMINAR USUARIO
=============================================*/
$(".tablas").on("click", ".btnEliminarUsuario", function () {

	var idUsuario = $(this).attr("idUsuario");
	var fotoUsuario = $(this).attr("fotoUsuario");
	var usuario = $(this).attr("usuario");

	Swal.fire({
		title: '¿Está seguro de borrar el usuario?',
		text: "¡Si no lo está puede cancelar la accíón!",
		type: 'warning',
		showCancelButton: true,
		confirmButtonColor: '#3085d6',
		cancelButtonColor: '#d33',
		cancelButtonText: 'Cancelar',
		confirmButtonText: 'Si, borrar usuario!'
	}).then(function (result) {

		if (result.value) {


			$.ajax({
				url: '/delete_user',
				type: 'POST',
				contentType: 'application/json',
				data: JSON.stringify({ idUsuario: idUsuario }),
				success: function (response) {
					Swal.fire(
						'¡Borrado!',
						'El usuario ha sido borrado.',
						'success'
					).then(() => {
						// Recargar la página para actualizar la lista de usuarios
						location.reload();
					});
				},
				error: function (xhr, status, error) {
					Swal.fire(
						'Error',
						'Hubo un problema al borrar el usuario.',
						'error'
					);
				}
			});

		}

	})

})




$('#userForm input').on("change", function () {
	console.log($(this).attr('value')); // based on the value do something.

	var dato = $(this).attr('value');

	if (dato == "masculino") {

		$(".previsualizar").attr("src", "../assets/images/hombre.png");

		// Asigna la ruta al input file
		$('#nuevaFotoOculta').val("../assets/images/hombre.png");



	}
	else if (dato == "femenino") {

		$(".previsualizar").attr("src", "../assets/images/mujer.png");

		$('#nuevaFotoOculta').val("../assets/images/mujer.png");

	}

	// Redimensionar la imagen a 512x512 píxeles
	$(".previsualizar").css({
		width: "80px",
		height: "80px",
		objectFit: "cover" // Mantener la relación de aspecto de la imagen
	});

});





/*=============================================
ELIMINAR USUARIO
=============================================*/
$(".tablas").on("click", ".btnReporteUsuario", function () {

	var idUsuario = $(this).attr("idUsuario");

	Swal.fire({
		title: '¿Crear reporte de las pruebas realizadas?',
		text: "¡Si no lo está puede cancelar la accíón!",
		type: 'warning',
		showCancelButton: true,
		confirmButtonColor: '#3085d6',
		cancelButtonColor: '#d33',
		cancelButtonText: 'Cancelar',
		confirmButtonText: 'Si, crear!'
	}).then(function (result) {

		if (result) {


			$.ajax({
				url: '/reporte',
				type: 'POST',
				contentType: 'application/json',
				data: JSON.stringify({ idUsuario: idUsuario }),
				success: function (response) {


					if (response.status == "success") {
						Swal.fire(
							'¡PDF creado!',
							'El reporte se ha creado correctamente',
							'success'
						).then(() => {
							// Recargar la página para actualizar la lista de usuarios
							//location.reload();
						});
					}


				},
				error: function (xhr, status, error) {
					Swal.fire(
						'Error',
						'Hubo un problema al crear el reporte.',
						'error'
					);
				}
			});

		}

	})

})