' Declaración de arreglos globales para las rutas (30 posiciones: 0 al 29)
' En EPSON RC+, declarar (30) crea índices del 0 al 30.
Global Integer rutaH1(30)
Global Integer rutaH2(30)

Function main
    Motor On
    Power Low
    
    ' Velocidad y aceleración conservadoras para manipular huevos de forma segura
    Accel 100, 100
    Speed 100
    
    Home
    
    ' 1. Inicializar las rutas exactas del caballo (carga los índices en arreglos)
    Call InitRutas
    
    ' 2. Definición del ÚNICO Pallet (6 columnas x 5 filas)
    ' P0 = Origen, P1 = Extremo X, P2 = Extremo Y
    ' Esto crea la cuadrícula perfecta con centros cada 45mm
    Pallet 1, P0, P1, P2, 6, 5
    
    ' Variables para almacenar la posición actual física de cada huevo
    Integer posH1, posH2
    posH1 = rutaH1(0) ' Huevo 1 inicia en índice 1 (Extremo Origen)
    posH2 = rutaH2(0) ' Huevo 2 inicia en índice 30 (Extremo Opuesto)
    
    ' --- Imprimir estado inicial en consola ---
    Print "========================================"
    Print "INICIO DE SECUENCIA: SALTOS DE CABALLO"
    Print "Huevo 1 inicia en posicion: ", posH1
    Print "Huevo 2 inicia en posicion: ", posH2
    Print "========================================"
    
    Integer i
    ' 3. Ciclo principal: 29 saltos de caballo alternados
    For i = 1 To 29
        Print "--- INICIANDO PASO ", i, " DE 29 ---"
        
        ' --- TURNO HUEVO 1 ---
        ' Ir a donde está el Huevo 1 y agarrarlo (60 mm por encima de la mesa)
        Jump Pallet(1, posH1) +Z(0)
        Call AgarrarHuevo
        
        ' Saltar a la nueva posición y bajar hasta los mismos 60 mm para no soltarlo de golpe ni aplastarlo
        Jump Pallet(1, rutaH1(i)) +Z(0)
        Call SoltarHuevo
        
        ' Actualizar la memoria de dónde quedó el Huevo 1 y mostrarlo
        posH1 = rutaH1(i)
        Print "   Movimiento ", i, ": Huevo 1 movido a la posicion ", posH1
        
        ' --- TURNO HUEVO 2 ---
        ' Ir a donde está el Huevo 2 y agarrarlo (60 mm por encima de la mesa)
        Jump Pallet(1, posH2) +Z(0)
        Call AgarrarHuevo
        
        ' Saltar a la nueva posición según el patrón matemático en reversa
        Jump Pallet(1, rutaH2(i)) +Z(0)
        Call SoltarHuevo
        
        ' Actualizar la memoria de dónde quedó el Huevo 2 y mostrarlo
        posH2 = rutaH2(i)
        Print "   Movimiento ", i, ": Huevo 2 movido a la posicion ", posH2
        
    Next
    
    ' 4. Finalizar rutina volviendo a una posición segura
    Print "========================================"
    Print "SECUENCIA COMPLETADA CON EXITO"
    Print "========================================"
    Home
    
Fend

' ==========================================
' Subrutinas de Control de la Ventosa (Lógica Negada)
' ==========================================

Function AgarrarHuevo
    ' Lógica Negada: Apaga el puerto 9 para activar la ventosa
    Off 9
    
    ' Sw(9) lee el estado de la entrada física 9. Espera hasta 1.5s.
    Wait Sw(9) = Off, 1.5
    
    ' Pequeña pausa mecánica (200ms) para que la succión estabilice la cáscara
    Wait 0.2
Fend

Function SoltarHuevo
    ' Lógica Negada: Enciende el puerto 9 para desactivar el vacío
    On 9
    
    ' Tiempo (500ms) para asegurar que el vacío se rompió y el huevo bajó suavemente
    Wait 0.5
Fend


' ==========================================
' Secuencias de Movimiento Matemático (Open Knight's Tour)
' ==========================================


Function InitRutas
    ' RUTA HUEVO 1 (Salto de Caballo Perfecto 6x5 validado)
    rutaH1(0) = 1
    rutaH1(1) = 9
    rutaH1(2) = 5
    rutaH1(3) = 18
    rutaH1(4) = 29
    rutaH1(5) = 21
    rutaH1(6) = 25
    rutaH1(7) = 14
    rutaH1(8) = 3
    rutaH1(9) = 7
    rutaH1(10) = 20
    rutaH1(11) = 28
    rutaH1(12) = 24
    rutaH1(13) = 11
    rutaH1(14) = 22
    rutaH1(15) = 30
    rutaH1(16) = 17
    rutaH1(17) = 6
    rutaH1(18) = 10
    rutaH1(19) = 2
    rutaH1(20) = 13
    rutaH1(21) = 26
    rutaH1(22) = 15
    rutaH1(23) = 4
    rutaH1(24) = 12
    rutaH1(25) = 23
    rutaH1(26) = 27
    rutaH1(27) = 19
    rutaH1(28) = 8
    rutaH1(29) = 16

    ' RUTA HUEVO 2 (Simetría radial exacta: 31 - posición de H1)
    rutaH2(0) = 30
    rutaH2(1) = 22
    rutaH2(2) = 26
    rutaH2(3) = 13
    rutaH2(4) = 2
    rutaH2(5) = 10
    rutaH2(6) = 6
    rutaH2(7) = 17
    rutaH2(8) = 28
    rutaH2(9) = 24
    rutaH2(10) = 11
    rutaH2(11) = 3
    rutaH2(12) = 7
    rutaH2(13) = 20
    rutaH2(14) = 9
    rutaH2(15) = 1
    rutaH2(16) = 14
    rutaH2(17) = 25
    rutaH2(18) = 21
    rutaH2(19) = 29
    rutaH2(20) = 18
    rutaH2(21) = 5
    rutaH2(22) = 16
    rutaH2(23) = 27
    rutaH2(24) = 19
    rutaH2(25) = 8
    rutaH2(26) = 4
    rutaH2(27) = 12
    rutaH2(28) = 23
    rutaH2(29) = 15
Fend
