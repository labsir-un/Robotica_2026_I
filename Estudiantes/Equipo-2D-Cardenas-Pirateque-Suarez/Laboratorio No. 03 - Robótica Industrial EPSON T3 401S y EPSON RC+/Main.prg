' =======================================================
'  CONFIGURACIÓN DE SEPARACIÓN Y ALTURA (Modifica aquí fácilmente)
' =======================================================
#define SEP_X 50.0  ' Reducido a 40 para no exceder los +/-100mm seguros en X
#define SEP_Y 50.0  ' Distancia en mm entre filas (Eje Y) En total 100mm (200 a 300)
#define ALTURA_Z -70.0 'Manipula aquí hasta dónde baja el robot (en mm)
' =======================================================

Global Integer i, k, curA, curB, r, c, visitedCount
Global Integer pathA(33), pathB(33), visited(31)

Function CargarRutas
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
    pathA(16) = 30
    pathA(17) = 17
    pathA(18) = 6
    pathA(19) = 10
    pathA(20) = 2
    pathA(21) = 13
    pathA(22) = 26
    pathA(23) = 15
    pathA(24) = 19
    pathA(25) = 8
    pathA(26) = 4
    pathA(27) = 12
    pathA(28) = 16
    pathA(29) = 27
    pathA(30) = 23
    pathA(31) = 23
    pathA(32) = 23

    pathB(1) = 30
    pathB(2) = 17
    pathB(3) = 6
    pathB(4) = 10
    pathB(5) = 2
    pathB(6) = 13
    pathB(7) = 26
    pathB(8) = 15
    pathB(9) = 19
    pathB(10) = 8
    pathB(11) = 4
    pathB(12) = 12
    pathB(13) = 16
    pathB(14) = 27
    pathB(15) = 23
    pathB(16) = 27
    pathB(17) = 14
    pathB(18) = 1
    pathB(19) = 9
    pathB(20) = 5
    pathB(21) = 18
    pathB(22) = 29
    pathB(23) = 21
    pathB(24) = 25
    pathB(25) = 14
    pathB(26) = 3
    pathB(27) = 7
    pathB(28) = 20
    pathB(29) = 28
    pathB(30) = 24
    pathB(31) = 11
    pathB(32) = 22
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
    Print prefijo$, " idx=", idx, " -> (col=", c, ", fila=", r, ")"
Fend

Function Paletizado_01
    Pallet 1, P0, P1, P2, 6, 5
    Call CargarRutas
    
    For i = 1 To 30
        visited(i) = 0
    Next
    visitedCount = 0
    
    curA = pathA(1)
    curB = pathB(1)
    Call MarcarVisitado(curA)
    Call MarcarVisitado(curB)
    
    Print "Inicio cabalgado 2-huevos: matriz 6x5"
    Call ImprimeIdx("H1 inicia en", curA)
    Call ImprimeIdx("H2 inicia en", curB)
    
    For k = 2 To 32
        Call ImprimeIdx("H1: regresa a (PICK)", curA)
        Call MarcarVisitado(curA)
        Jump Pallet(1, curA)
        On 9
        Wait 0.1
        Call ImprimeIdx("H1: va a (PLACE)", pathA(k))
        Call MarcarVisitado(pathA(k))
        Jump Pallet(1, pathA(k))
        Off 9
        Wait 0.1
        curA = pathA(k)

        Call ImprimeIdx("H2: regresa a (PICK)", curB)
        Call MarcarVisitado(curB)
        Jump Pallet(1, curB)
        On 9
        Wait 0.1
        Call ImprimeIdx("H2: va a (PLACE)", pathB(k))
        Call MarcarVisitado(pathB(k))
        Jump Pallet(1, pathB(k))
        Off 9
        Wait 0.1
        curB = pathB(k)
    Next
    
    Off 9
    Print "Fin: visitados unicos totales = ", visitedCount, "/30"
    
    Print "Esperando accion del operador para regresar a Home..."
      
    Print "Regresando a Home..."
    Home
Fend

Function main
    Real totalAncho, totalLargo

    Motor On
    Power High
    Accel 100, 100
    Speed 100
    
    ' El programa lee automáticamente los valores definidos arriba
    totalAncho = 5 * SEP_X  ' 6 columnas = 5 espacios intermedios
    totalLargo = 4 * SEP_Y  ' 5 filas = 4 espacios intermedios
    
    ' Configurar el Home en pulsos (J1 = 204800, el resto en 0)
    HomeSet 204800, 0, 0, 0
    
    ' Mover el robot físicamente al Home definido antes de iniciar
    Home
    
    ' Generación automática y centrada de los puntos del Pallet usando ALTURA_Z
    P0 = XY(-totalAncho / 2, 150, ALTURA_Z, 50)       ' Origen inferior izquierdo
    P1 = XY(totalAncho / 2, 150, ALTURA_Z, 50)        ' Esquina inferior derecha
    P2 = XY(-totalAncho / 2, 150 + totalLargo, ALTURA_Z, 50) ' Esquina superior izquierda
    
    Call Paletizado_01
Fend
