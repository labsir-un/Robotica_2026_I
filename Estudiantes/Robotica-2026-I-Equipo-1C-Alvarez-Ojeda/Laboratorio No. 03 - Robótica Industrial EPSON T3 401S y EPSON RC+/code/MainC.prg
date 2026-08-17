Global Integer i

Function main
	Motor On ' Encender los motores 
	Power High
	Accel 100, 100 ' Aceleración positiva y negativa al 100%
	Speed 100 ' Velocidad al 100%
	Home
	
	Call palletized
	
	Home
Fend


Function palletized

	Integer A(30)
	Integer B(30)

	Pallet 1, Origin, PointX, PointY, 6, 5

	' Secuencia Huevo A
	A(1) = 1
	A(2) = 14
	A(3) = 25
	A(4) = 21
	A(5) = 29
	A(6) = 18
	A(7) = 5
	A(8) = 9
	A(9) = 13
	A(10) = 26
	A(11) = 22
	A(12) = 30
	A(13) = 17
	A(14) = 6
	A(15) = 10
	A(16) = 2
	A(17) = 15
	A(18) = 28
	A(19) = 24
	A(20) = 11
	A(21) = 3
	A(22) = 7
	A(23) = 20
	A(24) = 16
	A(25) = 27
	A(26) = 23
	A(27) = 12
	A(28) = 4
	A(29) = 8
	A(30) = 19


	' Secuencia Huevo B
	B(1) = 30
	B(2) = 17
	B(3) = 6
	B(4) = 10
	B(5) = 2
	B(6) = 13
	B(7) = 26
	B(8) = 22
	B(9) = 18
	B(10) = 29
	B(11) = 21
	B(12) = 25
	B(13) = 14
	B(14) = 1
	B(15) = 9
	B(16) = 5
	B(17) = 16
	B(18) = 3
	B(19) = 7
	B(20) = 20
	B(21) = 28
	B(22) = 24
	B(23) = 11
	B(24) = 15
	B(25) = 4
	B(26) = 8
	B(27) = 19
	B(28) = 27
	B(29) = 23
	B(30) = 12


	' Movimiento intercalado
	For i = 1 To 29

		' Huevo A
		Jump Pallet(1, A(i))
		Wait 2
		Off DO_09 ' Agarra
		Wait 2

		Jump Pallet(1, A(i + 1))
		Wait 2
		On DO_09 ' Suelta
		Wait 2


		' Huevo B
		Jump Pallet(1, B(i))
		Wait 2
		Off DO_09 ' Agarra
		Wait 2

		Jump Pallet(1, B(i + 1))
		Wait 2
		On DO_09 ' Suelta
		Wait 2

	Next i

Fend