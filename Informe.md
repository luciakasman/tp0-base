

## Ejercicio 5:

Para resolver el ejercicio 5 se definió un protocolo de envío de mensajes que usa TCP en la capa de transporte.
Cada agencia se define como un cliente, habiendo 5 agencias. Cada una recibe como variables de entorno los campos que representan la apuesta de una persona: nombre, apellido, DNI, nacimiento y numero apostado.

Hay dos tipos de mensajes: 
* uno envía los campos al servidor para dejar registrada la apuesta.
* otro es la confirmación del servidor de que recibió correctamente la apuesta.

### Definición de un protocolo para el envío de los mensajes:

Los mensajes estarán en Big Endian y tendrán la forma:

` | código | agencia | datos | `

A su vez, cuando se desea registrar una apuesta el campo `datos` serán de la forma:

` "nombre","apellido","documento","nacimiento","número" `

Estos siempre tendrán el mismo orden y los campos estarán separados por comas.

El código podrá ser alguno de los siguientes:
* 0: se quiere registrar una apuesta.
* 1: la apuesta se registró de manera correcta.
* 2: hubo un error al registrar la apuesta.

Para los códigos 1 y 2 el campo `datos` estará vacío.

### Capa de comunicación:

La capa de comunicación está sobre la capa de transporte TPC. Esta implementa las funciones send y receive para la comunicación entre los sockets, evitando los fenómenos conocidos como short read y short write.





