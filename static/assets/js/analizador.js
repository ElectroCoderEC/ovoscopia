/*=============================================
			AL INICIAR LA PAGINA
=============================================*/
$(document).ready(function () {

	function updateValue(inputId, labelId) {
		$('#' + labelId).text($('#' + inputId).val());
		$('#' + inputId).on('input', function () {
			$('#' + labelId).text($(this).val());

			$.ajax({
				url: '/set_controles',
				method: 'POST',
				contentType: 'application/json',
				data: JSON.stringify({ "control": inputId, "valor": $('#' + inputId).val() }),
				success: function (response) {
					// Puedes manejar la respuesta si es necesario
					console.log(response.message);
				}
			});

		});

	}


	function defaultValue(inputId, labelId) {

		$('#' + labelId).text($('#' + inputId).val());

		$.ajax({
			url: '/set_controles',
			method: 'POST',
			contentType: 'application/json',
			data: JSON.stringify({ "control": inputId, "valor": $('#' + inputId).val() }),
			success: function (response) {
				// Puedes manejar la respuesta si es necesario
				console.log(response.message);
			}
		});

	}

	updateValue('lower-h', 'lower-h-val');
	updateValue('lower-s', 'lower-s-val');
	updateValue('lower-v', 'lower-v-val');
	updateValue('upper-h', 'upper-h-val');
	updateValue('upper-s', 'upper-s-val');
	updateValue('upper-v', 'upper-v-val');

	updateValue('lower-h-dedos', 'lower-h-dedos-val');
	updateValue('lower-s-dedos', 'lower-s-dedos-val');
	updateValue('lower-v-dedos', 'lower-v-dedos-val');
	updateValue('upper-h-dedos', 'upper-h-dedos-val');
	updateValue('upper-s-dedos', 'upper-s-dedos-val');
	updateValue('upper-v-dedos', 'upper-v-dedos-val');

	$('#btnDefault').click(function () {


		/*
		$('#lower-h').val(30)
		$('#lower-s').val(16)
		$('#lower-v').val(103)

		$('#upper-h').val(94)
		$('#upper-s').val(255)
		$('#upper-v').val(255)

		$('#lower-h-dedos').val(40)
		$('#lower-s-dedos').val(16)
		$('#lower-v-dedos').val(87)

		$('#upper-h-dedos').val(100)
		$('#upper-s-dedos').val(255)
		$('#upper-v-dedos').val(255)
		*/

		$.ajax({
			url: '/get_hsv',
			type: 'POST',
			contentType: 'application/json',
			data: JSON.stringify({
				"lower-h": $('#lower-h').val(),
				"lower-s": $('#lower-s').val(),
				"lower-v": $('#lower-v').val(),
				"upper-h": $('#upper-h').val(),
				"upper-s": $('#upper-s').val(),
				"upper-v": $('#upper-v').val(),
				"lower-h-dedos": $('#lower-h-dedos').val(),
				"lower-s-dedos": $('#lower-s-dedos').val(),
				"lower-v-dedos": $('#lower-v-dedos').val(),
				"upper-h-dedos": $('#upper-h-dedos').val(),
				"upper-s-dedos": $('#upper-s-dedos').val(),
				"upper-v-dedos": $('#upper-v-dedos').val()

			}),
			success: function (response) {

				if (response.status == "success") {


				}
				else {
					Swal.fire(
						'Error',
						'Hubo un problema al obtener de configuracion los valores: ' + response.message,
						'error'
					);
				}



			},
			error: function (xhr, status, error) {
				Swal.fire(
					'Error',
					'Hubo un problema al actualizar los valores: ' + error,
					'error'
				);
			}
		});


		defaultValue("lower-h", 'lower-h-val')
		defaultValue("lower-s", 'lower-s-val')
		defaultValue("lower-v", 'lower-v-val')
		defaultValue("upper-h", 'upper-h-val')
		defaultValue("upper-s", 'upper-s-val')
		defaultValue("upper-v", 'upper-v-val')

		defaultValue("lower-h-dedos", 'lower-h-dedos-val')
		defaultValue("lower-s-dedos", 'lower-s-dedos-val')
		defaultValue("lower-v-dedos", 'lower-v-dedos-val')
		defaultValue("upper-h-dedos", 'upper-h-dedos-val')
		defaultValue("upper-s-dedos", 'upper-s-dedos-val')
		defaultValue("upper-v-dedos", 'upper-v-dedos-val')
	});


	$('#btnSaveValues').click(function () {

		Swal.fire({
			title: '¿Está seguro que desea guardar estos valores HSV?',
			text: "¡Si no lo está puede cancelar la accíón!",
			type: 'warning',
			showCancelButton: true,
			confirmButtonColor: '#3085d6',
			cancelButtonColor: '#d33',
			cancelButtonText: 'Cancelar',
			confirmButtonText: 'Si, guardar!'
		}).then(function (result) {

			if (result.value) {

				$.ajax({
					url: '/save_hsv',
					type: 'POST',
					contentType: 'application/json',
					data: JSON.stringify({
						"lower-h": $('#lower-h').val(),
						"lower-s": $('#lower-s').val(),
						"lower-v": $('#lower-v').val(),
						"upper-h": $('#upper-h').val(),
						"upper-s": $('#upper-s').val(),
						"upper-v": $('#upper-v').val(),
						"lower-h-dedos": $('#lower-h-dedos').val(),
						"lower-s-dedos": $('#lower-s-dedos').val(),
						"lower-v-dedos": $('#lower-v-dedos').val(),
						"upper-h-dedos": $('#upper-h-dedos').val(),
						"upper-s-dedos": $('#upper-s-dedos').val(),
						"upper-v-dedos": $('#upper-v-dedos').val()

					}),
					success: function (response) {

						if (response.status == "success") {
							Swal.fire(
								'¡Guardado!',
								'Los nuevos valores HSV fueron actualizados',
								'success'
							).then(() => {
								// Recargar la página para actualizar la lista de usuarios
								//location.reload();
							});
						}
						else {
							Swal.fire(
								'Error',
								'Hubo un problema al actualizar los valores: ' + response.message,
								'error'
							);
						}



					},
					error: function (xhr, status, error) {
						Swal.fire(
							'Error',
							'Hubo un problema al actualizar los valores: ' + error,
							'error'
						);
					}
				});

			}

		})


	});


	function isEmpty(str) {
		return (!str || str.length === 0);
	}




	var txtTipo = "";
	var txtEstado = "";
	var txtVencimiento = "";


	const socket = io.connect('http://' + document.domain + ':' + location.port);
	// Escuchar los mensajes del servidor
	socket.on("connect_error", (error) => {
		console.error("Error de conexión:", error);
	});


	var bandaON = false;
	var bandaOFF = false;
	var isRegistro = false;


	socket.on('update', function (data) {
		// Separar datos del mensaje

		//console.log("Datos recibidos:", data.sms);
		// Actualizar tus labels aquí...


		if (data.TIPO.length > 2) {
			$('#txtTIPO').text(data.TIPO);
			//console.log(data.TIPO);
			txtTipo = data.TIPO;
		}



		var datos = data.sms

		const partes = datos.split('/');


		if (partes.length >= 7) {

			if (partes[5] == "0") {

				if (bandaON == false) {
					bandaON = true;
					bandaOFF = false;
					$("#imgBanda").attr("src", "../assets/images/banda.png");
				}

			}

			else if (partes[5] == "1") {

				if (bandaOFF == false) {
					bandaON = false;
					bandaOFF = true;
					$("#imgBanda").attr("src", "../assets/images/banda.gif");
				}


			}



			if (partes[2] == "1" && partes[4] == "OVO") {
				$('#txtColocar').css('background-color', 'green');
				$('#texto_estado').text('PROCESO INICIADO');
			}


			if (partes[3] == "0" && partes[4] == "INICIO") {
				$('#txtColocar').css('background-color', 'orange');
				$('#texto_estado').text('COLOQUE EL HUEVO EN LA BANDA');
			}

			if (partes[3] == "1" && partes[4] == "INICIO") {
				$('#txtColocar').css('background-color', 'red');
				$('#texto_estado').text('ESPERE A LA POSICIÓN INICIAL');

				$('#txtTIPO').text("Tipo de Huevo");
				$('#txtESTADO').text("---");

				$("#imgHuevo").attr("src", "../assets/images/noHuevo2.png");

				$('#txtFecha').text("---");

				$('#txtResultado').text("RESULTADO");

				isRegistro = false;

			}


			if (partes[1] == "1" && partes[4] == "MEDIO") {
				$('#txtColocar').css('background-color', 'yellow');

				$('#texto_estado').text('ANALIZANDO...');
				$('#texto_estado').css('color', 'black');
			}



			if (partes[4] == "CLASIFICADO") {
				$('#txtColocar').css('background-color', 'purple');
				$('#texto_estado').text('CLASIFICADO');
				$('#texto_estado').css('color', 'white');


				if (!isRegistro) {

					isRegistro = true;


					fetch("/registrar_ovoscopia", {
						method: "POST",
						headers: {
							"Content-Type": "application/json"
						},
						body: JSON.stringify({
							tipo: txtTipo,
							estado: txtEstado,
							vencimiento: txtVencimiento
						})
					})
						.then(response => response.json())
						.then(data => {
							console.log("Respuesta del servidor:", data);
						})
						.catch(error => {
							console.error("Error:", error);
						});

				}


			}


			if (partes[4] == "FINAL") {
				$('#txtColocar').css('background-color', 'cyan');
				$('#texto_estado').text('RETIRE EL HUEVO DE LA BANDA');
				$('#texto_estado').css('color', 'black');
			}
			if (partes[0] == "0" && partes[1] == "0" && partes[2] == "0" && partes[4] == "INICIO") {
				$('#texto_estado').css('color', 'white');
			}



			if (data.ESTADO.length > 2) {



				if (data.ESTADO == "EMBRIÓN") {

					txtEstado = "FÉRTIL";
					$('#txtESTADO').text(txtEstado);

					if (txtTipo == "NORMAL" || txtTipo == "OTRO") {
						$("#imgHuevo").attr("src", "../assets/images/fertil.png");
					}
					else {
						$("#imgHuevo").attr("src", "../assets/images/whitefertil.png");
					}



					if (data.VENCIMIENTO.length > 2) {
						$('#txtFecha').text(data.VENCIMIENTO);
						$('#txtFecha').css('color', 'green');

						$('#txtResultado').text("RESULTADO | Límite para incubación: 7-10 días");

						txtVencimiento = data.VENCIMIENTO;

					}
				}

				if (data.ESTADO == "CONSUMO") {

					txtEstado = data.ESTADO;
					$('#txtESTADO').text(data.ESTADO);


					if (txtTipo == "NORMAL" || txtTipo == "OTRO") {
						$("#imgHuevo").attr("src", "../assets/images/consumible.png");
					}
					else {
						$("#imgHuevo").attr("src", "../assets/images/whiteconsumible.png");
					}


					if (data.VENCIMIENTO.length > 2) {
						$('#txtFecha').text(data.VENCIMIENTO);
						$('#txtFecha').css('color', 'green');

						$('#txtResultado').text("RESULTADO | Fecha de Vencimiento: +21 días");
						txtVencimiento = data.VENCIMIENTO;

					}
				}

				if (data.ESTADO == "MALO") {

					txtEstado = data.ESTADO;
					$('#txtESTADO').text(data.ESTADO);

					if (txtTipo == "NORMAL" || txtTipo == "OTRO") {
						$("#imgHuevo").attr("src", "../assets/images/malo.png");
					}
					else {
						$("#imgHuevo").attr("src", "../assets/images/whitemalo.png");
					}



					if (data.VENCIMIENTO.length > 2) {
						$('#txtFecha').text("NO SE PUEDE CONSUMIR!");
						$('#txtFecha').css('color', 'red');

						$('#txtResultado').text("RESULTADO");

						txtVencimiento = "---";
					}
				}



			}














		}

	});




	$('#siImagen').click(function () {
		var estadoCheck = "False"

		if ($(this).is(':checked') == true) {
			//alert(estadoCheck);
			estadoCheck = "True"
		} else {
			//alert(estadoCheck);
			estadoCheck = "False"
		}

		$.ajax({
			url: '/set_check',
			method: 'POST',
			contentType: 'application/json',
			data: JSON.stringify({ check: estadoCheck }),
			success: function (response) {
				// Puedes manejar la respuesta si es necesario
				console.log(response.message);
			}
		});

	});


	$('#btnCapturar').click(function () {
		$.ajax({
			url: '/set_imagen',
			method: 'POST',
			contentType: 'application/json',
			data: JSON.stringify({ estado: "ON" }),
			success: function (response) {
				// Puedes manejar la respuesta si es necesario
				console.log(response.message);
			}
		});
	});


	$('#btnReproducir').click(function () {
		$.ajax({
			url: '/set_imagen',
			method: 'POST',
			contentType: 'application/json',
			data: JSON.stringify({ estado: "OFF" }),
			success: function (response) {
				// Puedes manejar la respuesta si es necesario
				console.log(response.message);
			}
		});
	});


	$('#btnGuardar').click(function () {

		var cedula = $('#formCedula').text();
		var rutaFoto = ""

		$.ajax({
			url: '/save_imagen_procesada',
			method: 'POST',
			contentType: 'application/json',
			data: JSON.stringify({ cedula: cedula }),
			success: function (response) {
				// Puedes manejar la respuesta si es necesario
				console.log(response.message);
				rutaFoto = response.foto;

			}
		});



		Swal.fire({
			title: '¿Está seguro que deseas guardar esta prueba?',
			text: "¡Si no lo está puede cancelar la accíón!",
			type: 'warning',
			showCancelButton: true,
			confirmButtonColor: '#3085d6',
			cancelButtonColor: '#d33',
			cancelButtonText: 'Cancelar',
			confirmButtonText: 'Si, guardar!'
		}).then(function (result) {

			if (result.value) {

				$.ajax({
					url: '/set_guardar',
					type: 'POST',
					contentType: 'application/json',
					data: JSON.stringify({
						"idUsuario": $('#formID').val(),
						"xI": $('#xLeft').val(),
						"yI": $('#yLeft').val(),
						"valorIzquierdo": $('#valorIzquierdo').text(),
						"tipoIzquierdo": $('#tipoIzquierdo').text(),
						"xD": $('#xRight').val(),
						"yD": $('#yRight').val(),
						"valorDerecho": $('#valorDerecho').text(),
						"tipoDerecho": $('#tipoDerecho').text(),
						"foto": rutaFoto,
					}),
					success: function (response) {

						if (response.status == "success") {
							Swal.fire(
								'¡Guardado!',
								'La prueba se guardo correctamente',
								'success'
							).then(() => {
								// Recargar la página para actualizar la lista de usuarios
								//location.reload();
							});
						}
						else {
							Swal.fire(
								'Error',
								'Hubo un problema al guardar la prueba: ' + response.message,
								'error'
							);
						}
					},
					error: function (xhr, status, error) {
						Swal.fire(
							'Error',
							'Hubo un problema al guardar la prueba: ' + error,
							'error'
						);
					}
				});
			}
		})
	});





	$('.tipoVideo').on('change', function () {
		console.log(this.value);
		const selectedValue = this.value;

		if (selectedValue == "normal") {
			$('#contenedorControles').hide();
			$('#contenedorPies').hide();
			$('#contenedorBotones').hide();
		}

		else {
			$('#contenedorControles').show();
			$('#contenedorPies').show();
			$('#contenedorBotones').show();
		}

		$.ajax({
			url: '/set_mode',
			method: 'POST',
			contentType: 'application/json',
			data: JSON.stringify({ mode: selectedValue }),
			success: function (response) {
				// Puedes manejar la respuesta si es necesario
				console.log(response.message);
			}
		});

	});


});


