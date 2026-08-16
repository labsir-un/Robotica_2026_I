' ==============================================
'  Movimiento alternado de dos huevos
'  Recorrido sobre una matriz 6x5
' ==============================================

Global Integer i
Global Integer k
Global Integer curA
Global Integer curB
Global Integer pathA(32)
Global Integer pathB(32)

Global Integer visited(30)
Global Integer visitedCount
Global Integer r, c

Function CargarRutas

    ' Ruta del primer huevo
    pathA(1) = 1
    pathA(2) = 9
    pathA(3) = 5
    pathA(4) = 18
    pathA(5) = 29
    pathA(6) = 21
    pathA(7) = 25
    pathA(8) = 14
    pathA(9) = 3
    pathA(10) = 7
    pathA(11) = 20
    pathA(12) = 28
    pathA(13) = 24
    pathA(14) = 11
    pathA(15) = 22
    pathA(16) = 26
    pathA(17) = 13
    pathA(18) = 2
    pathA(19) = 15
    pathA(20) = 19
    pathA(21) = 8
    pathA(22) = 4
    pathA(23) = 12
    pathA(24) = 16
    pathA(25) = 27
    pathA(26) = 23
    pathA(27) = 10
    pathA(28) = 6
    pathA(29) = 17
    pathA(30) = 30

    ' Ruta del segundo huevo
    pathB(1) = 30
    pathB(2) = 22
    pathB(3) = 26
    pathB(4) = 13
    pathB(5) = 2
    pathB(6) = 10
    pathB(7) = 6
    pathB(8) = 17
    pathB(9) = 1
    pathB(10) = 28
    pathB(11) = 24
    pathB(12) = 11
    pathB(13) = 3
    pathB(14) = 7
    pathB(15) = 20
    pathB(16) = 9
    pathB(17) = 5
    pathB(18) = 18
    pathB(19) = 29
    pathB(20) = 16
    pathB(21) = 12
    pathB(22) = 23
    pathB(23) = 27
    pathB(24) = 19
    pathB(25) = 15
    pathB(26) = 4
    pathB(27) = 8
    pathB(28) = 21
    pathB(29) = 24
    pathB(30) = 14

Fend

Function MarcarVisitado(idx As Integer)

    If visited(idx) = 0 Then
        visited(idx) = 1
        visitedCount = visitedCount + 1
    EndIf

Fend

Function ImprimeIdx(prefijo$ As String, idx As Integer)

    r = (idx - 1) / 6 + 1
    c = idx - (r - 1) * 6

Fend

Function Paletizado_01

    ' Configuración del pallet
    Pallet 1, Origen, PuntoX, PuntoY, 6, 5

    ' Cargar las secuencias
    Call CargarRutas

    ' Reiniciar el registro de posiciones
    For i = 1 To 30
        visited(i) = 0
    Next

    visitedCount = 0

    ' Posiciones iniciales
    curA = pathA(1)
    curB = pathB(1)

    Call MarcarVisitado(curA)
    Call MarcarVisitado(curB)

    ' Ejecutar los movimientos
    For k = 2 To 30

        ' Movimiento del primer huevo
        Call MarcarVisitado(curA)

        Jump Pallet(1, curA)

        On Out_9
        Wait 0.10

        Jump Pallet(1, pathA(k))

        Off Out_9
        Wait 0.10

        curA = pathA(k)

        ' Movimiento del segundo huevo
        Call MarcarVisitado(curB)

        Jump Pallet(1, curB)

        On Out_9
        Wait 0.10

        Jump Pallet(1, pathB(k))

        Off Out_9
        Wait 0.10

        curB = pathB(k)

    Next

    ' Finalizar el proceso
    Off Out_9
    Jump Origen
    Home

Fend

Function main

    Wait 0.1
    Motor On
    Power High
    Accel 100, 100
    Speed 100
	Tool 1
    Home

    Pallet 1, Origen, PuntoX, PuntoY, 6, 5

    Call Paletizado_01

Fend
