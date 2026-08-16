Function init
	Motor On
    Power High

    Speed 20
    Accel 30, 30
    
    Pallet 1, Origin, PointX, PointY, 5, 6
	On 9
Fend
Function Main
	Call init
    Integer i

    Integer filaA(30)
    Integer colA(30)
	Integer filaB(30)
    Integer colB(30)
	
    
    ' =====================================
    ' RECORRIDO DEL CABALLO
    ' =====================================

    filaA(1) = 1
	colA(1) = 1

	filaA(2) = 2
	colA(2) = 3

	filaA(3) = 1
	colA(3) = 5

	filaA(4) = 3
	colA(4) = 6

	filaA(5) = 5
	colA(5) = 5
	
	filaA(6) = 4
	colA(6) = 3
	
	filaA(7) = 5
	colA(7) = 1
	
	filaA(8) = 3
	colA(8) = 2
	
	filaA(9) = 1
	colA(9) = 3
	
	filaA(10) = 2
	colA(10) = 1
	
	filaA(11) = 4
	colA(11) = 2
	
	filaA(12) = 5
	colA(12) = 4
	
	filaA(13) = 4
	colA(13) = 6
	
	filaA(14) = 2
	colA(14) = 5
	
	filaA(15) = 4
	colA(15) = 4
	
	filaA(16) = 5
	colA(16) = 6
	
	filaA(17) = 3
	colA(17) = 5
	
	filaA(18) = 1
	colA(18) = 6
	
	filaA(19) = 2
	colA(19) = 4
	
	filaA(20) = 1
	colA(20) = 2
	
	filaA(21) = 3
	colA(21) = 1
	
	filaA(22) = 5
	colA(22) = 2
	
	filaA(23) = 3
	colA(23) = 3
	
	filaA(24) = 1
	colA(24) = 4
	
	filaA(25) = 2
	colA(25) = 2
	
	filaA(26) = 4
	colA(26) = 1
	
	filaA(27) = 5
	colA(27) = 3
	
	filaA(28) = 3
	colA(28) = 4
	
	filaA(29) = 2
	colA(29) = 6
	
	filaA(30) = 4
	colA(30) = 5
	
	filaB(1) = 5
	colB(1) = 6
	
	filaB(2) = 3
	colB(2) = 5
	
	filaB(3) = 1
	colB(3) = 6
	
	filaB(4) = 2
	colB(4) = 4
	
	filaB(5) = 1
	colB(5) = 2
	
	filaB(6) = 3
	colB(6) = 1
	
	filaB(7) = 5
	colB(7) = 2
	
	filaB(8) = 3
	colB(8) = 3
	
	filaB(9) = 1
	colB(9) = 4
	
	filaB(10) = 2
	colB(10) = 2
	
	filaB(11) = 4
	colB(11) = 1
	
	filaB(12) = 5
	colB(12) = 3
	
	filaB(13) = 4
	colB(13) = 5
	
	filaB(14) = 2
	colB(14) = 6
	
	filaB(15) = 3
	colB(15) = 4
	
	filaB(16) = 1
	colB(16) = 3
	
	filaB(17) = 2
	colB(17) = 1
	
	filaB(18) = 4
	colB(18) = 2
	
	filaB(19) = 5
	colB(19) = 4
	
	filaB(20) = 4
	colB(20) = 6
	
	filaB(21) = 2
	colB(21) = 5
	
	filaB(22) = 4
	colB(22) = 4
	
	filaB(23) = 2
	colB(23) = 3
	
	filaB(24) = 1
	colB(24) = 1
	
	filaB(25) = 3
	colB(25) = 2
	
	filaB(26) = 5
	colB(26) = 1
	
	filaB(27) = 4
	colB(27) = 3
	
	filaB(28) = 5
	colB(28) = 5
	
	filaB(29) = 3
	colB(29) = 6
	
	filaB(30) = 1
	colB(30) = 5
	Print "Go home "
    Home
	Print "Go p1 "
    Jump P1
	LimZ -50
	For i = 1 To 29
		Print "Paso ", i
	    ' Mover huevo A
	    
	    Jump Pallet(1, filaA(i), colA(i))
	    Wait 0.5
	    Off 9
	    Jump Pallet(1, filaA(i + 1), colA(i + 1))
	    Wait 0.5
	    On 9
		
	    ' Mover huevo B
	    
	    Jump Pallet(1, filaB(i), colB(i))
	    Wait 0.5
	    Off 9
	    Jump Pallet(1, filaB(i + 1), colB(i + 1))
	    Wait 0.5
	    On 9

	Next i

    Home

Fend
