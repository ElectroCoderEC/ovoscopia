/*=============================================
Data Table
=============================================*/

$(document).ready(function () {
	$(".tablas").DataTable({

		"language": {

			"sProcessing": "Procesando...",
			"sLengthMenu": "Mostrar _MENU_ registros",
			"sZeroRecords": "No se encontraron resultados",
			"sEmptyTable": "Ningún dato disponible en esta tabla",
			"sInfo": "Mostrando registros del _START_ al _END_ de un total de _TOTAL_",
			"sInfoEmpty": "Mostrando registros del 0 al 0 de un total de 0",
			"sInfoFiltered": "(filtrado de un total de _MAX_ registros)",
			"sInfoPostFix": "",
			"sSearch": "Buscar:",
			"sUrl": "",
			"sInfoThousands": ",",
			"sLoadingRecords": "Cargando...",
			"oPaginate": {
				"sFirst": "Primero",
				"sLast": "Último",
				"sNext": "Siguiente",
				"sPrevious": "Anterior"
			},
			"oAria": {
				"sSortAscending": ": Activar para ordenar la columna de manera ascendente",
				"sSortDescending": ": Activar para ordenar la columna de manera descendente"
			}

		}

	});



	$(".previsualizar").attr("src", "../assets/images/hombre.png");
	// Redimensionar la imagen a 512x512 píxeles
	$(".previsualizar").css({
		width: "80px",
		height: "80px",
		objectFit: "cover" // Mantener la relación de aspecto de la imagen
	});
	var rutaImagen = "../assets/images/hombre.png";
	// Asigna la ruta al input file
	$('#nuevaFotoOculta').val(rutaImagen);



});





