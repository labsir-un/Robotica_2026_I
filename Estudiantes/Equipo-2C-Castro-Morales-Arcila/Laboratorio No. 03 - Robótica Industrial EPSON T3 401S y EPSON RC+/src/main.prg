Global Integer fila_o
Global Integer col_o
Global Integer fila_d
Global Integer col_d

Function Main
    Motor On
    Power High
    Accel 100, 100
    Speed 100
    Wait 10
    Home
    Call SecuenciaMovimientos
    Home
Fend

Function MoverHuevo(huevo As Integer, origen As Integer, destino As Integer)
    Pallet 1, Origen, PuntoX, PuntoY, 6, 5
    
    Jump Pallet(1, origen)
    Move Pallet(1, origen) :Z(-90)
    On 9
    Wait 0.2
    Move Pallet(1, origen) :Z(0)

    Jump Pallet(1, destino)
    Move Pallet(1, destino) :Z(-90)
    Off 9
    Wait 0.2
    Move Pallet(1, destino) :Z(0)
Fend

Function SecuenciaMovimientos
   Call MoverHuevo(1, 1, 9)
   Call MoverHuevo(2, 30, 22)
   Call MoverHuevo(1, 9, 5)
   Call MoverHuevo(2, 22, 26)
   Call MoverHuevo(1, 5, 18)
   Call MoverHuevo(2, 26, 13)
   Call MoverHuevo(1, 18, 29)
   Call MoverHuevo(2, 13, 2)
   Call MoverHuevo(1, 29, 21)
   Call MoverHuevo(2, 2, 10)
   Call MoverHuevo(1, 21, 25)
   Call MoverHuevo(2, 10, 6)
   Call MoverHuevo(1, 25, 14)
   Call MoverHuevo(2, 6, 17)
   Call MoverHuevo(1, 14, 27)
   Call MoverHuevo(2, 17, 4)
   Call MoverHuevo(1, 27, 19)
   Call MoverHuevo(2, 4, 12)
   Call MoverHuevo(1, 19, 8)
   Call MoverHuevo(2, 12, 23)
   Call MoverHuevo(1, 8, 16)
   Call MoverHuevo(2, 23, 15)
   Call MoverHuevo(1, 16, 20)
   Call MoverHuevo(2, 15, 11)
   Call MoverHuevo(1, 20, 7)
   Call MoverHuevo(2, 11, 24)
   Call MoverHuevo(1, 7, 3)
   Call MoverHuevo(2, 24, 28)
   Call MoverHuevo(1, 3, 11)
   Call MoverHuevo(2, 28, 20)
   Call MoverHuevo(1, 11, 24)
   Call MoverHuevo(2, 20, 7)
   Call MoverHuevo(1, 24, 28)
   Call MoverHuevo(2, 7, 3)
   Call MoverHuevo(1, 28, 15)
   Call MoverHuevo(2, 3, 16)
   Call MoverHuevo(1, 15, 4)
   Call MoverHuevo(2, 16, 27)
   Call MoverHuevo(1, 4, 12)
   Call MoverHuevo(2, 27, 19)
   Call MoverHuevo(1, 12, 23)
   Call MoverHuevo(2, 19, 8)
   Call MoverHuevo(1, 23, 10)
   Call MoverHuevo(2, 8, 21)
   Call MoverHuevo(1, 10, 2)
   Call MoverHuevo(2, 21, 29)
   Call MoverHuevo(1, 2, 13)
   Call MoverHuevo(2, 29, 18)
   Call MoverHuevo(1, 13, 26)
   Call MoverHuevo(2, 18, 5)
   Call MoverHuevo(1, 26, 22)
   Call MoverHuevo(2, 5, 9)
   Call MoverHuevo(1, 22, 30)
   Call MoverHuevo(2, 9, 1)
   Call MoverHuevo(1, 30, 17)
   Call MoverHuevo(2, 1, 14)
   Call MoverHuevo(1, 17, 6)
   Call MoverHuevo(2, 14, 25)
Fend