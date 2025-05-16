
/*=============================================
EDITAR PLANTILLA
=============================================*/
$(".tablas").on("click", ".btnModificarPlantilla", function () {

	var idPlantilla = $(this).attr("idPlantilla");


	$.ajax({
		url: '/get_plantilla',
		type: 'POST',
		contentType: 'application/json',
		data: JSON.stringify({ idPlantilla: idPlantilla }),
		success: function (response) {
			var datos = response.plantilla[0]; // Acceder a la primera fila de resultados

			$("#idPlantilla").val(response.plantilla[0]);
			$("#editarPlantilla").val(response.plantilla[1]);
			$("#editarDescripcion").val(response.plantilla[2]);
		},
		error: function (xhr, status, error) {
			Swal.fire(
				'Error',
				'Hubo un problema al borrar este dato.',
				'error'
			);
		}
	});



})


/*=============================================
ELIMINAR PLANTILLA
=============================================*/
$(".tablas").on("click", ".btnEliminarPlantilla", function () {

	var idPlantilla = $(this).attr("idPlantilla");


	Swal.fire({
		title: '¿Está seguro de borrar este dato?',
		text: "¡Si no lo está puede cancelar la accíón!",
		type: 'warning',
		showCancelButton: true,
		confirmButtonColor: '#3085d6',
		cancelButtonColor: '#d33',
		cancelButtonText: 'Cancelar',
		confirmButtonText: 'Si, borrar plantilla!'
	}).then(function (result) {

		if (result.value) {


			$.ajax({
				url: '/delete_plantilla',
				type: 'POST',
				contentType: 'application/json',
				data: JSON.stringify({ idPlantilla: idPlantilla }),
				success: function (response) {
					Swal.fire(
						'¡Borrado!',
						'La plantilla ha sido borrada.',
						'success'
					).then(() => {
						// Recargar la página para actualizar la lista de usuarios
						location.reload();
					});
				},
				error: function (xhr, status, error) {
					Swal.fire(
						'Error',
						'Hubo un problema al borrar este dato.',
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


