Global Integer i

Function main
	Motor On ' encender los motores 
	Power High
	Accel 100, 100 '% acel. positiv y negativ del 100
	Speed 100 '%
	Home
	
	Call palletized
	
	Home
		
	
Fend

Function palletized
	Pallet 1, Origin, PointX, PointY, 6, 5

	Jump Pallet(1, 1) ' Huevo A1: 1 -> 14
	Wait 2
	Off DO_09
	Jump Pallet(1, 14)
	Wait 2
	On DO_09

	Jump Pallet(1, 30) ' Huevo B1: 30 -> 17
	Wait 2
	Off DO_09
	Jump Pallet(1, 17)
	Wait 2
	On DO_09

	Jump Pallet(1, 14) ' Huevo A2: 14 -> 25
	Wait 2
	Off DO_09
	Jump Pallet(1, 25)
	Wait 2
	On DO_09

	Jump Pallet(1, 17) ' Huevo B2: 17 -> 6
	Wait 2
	Off DO_09
	Jump Pallet(1, 6)
	Wait 2
	On DO_09

	Jump Pallet(1, 25) ' Huevo A3: 25 -> 21
	Wait 2
	Off DO_09
	Jump Pallet(1, 21)
	Wait 2
	On DO_09

	Jump Pallet(1, 6) ' Huevo B3: 6 -> 10
	Wait 2
	Off DO_09
	Jump Pallet(1, 10)
	Wait 2
	On DO_09

	Jump Pallet(1, 21) ' Huevo A4: 21 -> 29
	Wait 2
	Off DO_09
	Jump Pallet(1, 29)
	Wait 2
	On DO_09

	Jump Pallet(1, 10) ' Huevo B4: 10 -> 2
	Wait 2
	Off DO_09
	Jump Pallet(1, 2)
	Wait 2
	On DO_09

	Jump Pallet(1, 29) ' Huevo A5: 29 -> 18
	Wait 2
	Off DO_09
	Jump Pallet(1, 18)
	Wait 2
	On DO_09

	Jump Pallet(1, 2) ' Huevo B5: 2 -> 13
	Wait 2
	Off DO_09
	Jump Pallet(1, 13)
	Wait 2
	On DO_09

	Jump Pallet(1, 18) ' Huevo A6: 18 -> 5
	Wait 2
	Off DO_09
	Jump Pallet(1, 5)
	Wait 2
	On DO_09

	Jump Pallet(1, 13) ' Huevo B6: 13 -> 26
	Wait 2
	Off DO_09
	Jump Pallet(1, 26)
	Wait 2
	On DO_09

	Jump Pallet(1, 5) ' Huevo A7: 5 -> 9
	Wait 2
	Off DO_09
	Jump Pallet(1, 9)
	Wait 2
	On DO_09

	Jump Pallet(1, 26) ' Huevo B7: 26 -> 22
	Wait 2
	Off DO_09
	Jump Pallet(1, 22)
	Wait 2
	On DO_09

	Jump Pallet(1, 9) ' Huevo A8: 9 -> 13
	Wait 2
	Off DO_09
	Jump Pallet(1, 13)
	Wait 2
	On DO_09

	Jump Pallet(1, 22) ' Huevo B8: 22 -> 18
	Wait 2
	Off DO_09
	Jump Pallet(1, 18)
	Wait 2
	On DO_09

	Jump Pallet(1, 13) ' Huevo A9: 13 -> 26
	Wait 2
	Off DO_09
	Jump Pallet(1, 26)
	Wait 2
	On DO_09

	Jump Pallet(1, 18) ' Huevo B9: 18 -> 29
	Wait 2
	Off DO_09
	Jump Pallet(1, 29)
	Wait 2
	On DO_09

	Jump Pallet(1, 26) ' Huevo A10: 26 -> 22
	Wait 2
	Off DO_09
	Jump Pallet(1, 22)
	Wait 2
	On DO_09

	Jump Pallet(1, 29) ' Huevo B10: 29 -> 21
	Wait 2
	Off DO_09
	Jump Pallet(1, 21)
	Wait 2
	On DO_09

	Jump Pallet(1, 22) ' Huevo A11: 22 -> 30
	Wait 2
	Off DO_09
	Jump Pallet(1, 30)
	Wait 2
	On DO_09

	Jump Pallet(1, 21) ' Huevo B11: 21 -> 25
	Wait 2
	Off DO_09
	Jump Pallet(1, 25)
	Wait 2
	On DO_09

	Jump Pallet(1, 30) ' Huevo A12: 30 -> 17
	Wait 2
	Off DO_09
	Jump Pallet(1, 17)
	Wait 2
	On DO_09

	Jump Pallet(1, 25) ' Huevo B12: 25 -> 14
	Wait 2
	Off DO_09
	Jump Pallet(1, 14)
	Wait 2
	On DO_09

	Jump Pallet(1, 17) ' Huevo A13: 17 -> 6
	Wait 2
	Off DO_09
	Jump Pallet(1, 6)
	Wait 2
	On DO_09

	Jump Pallet(1, 14) ' Huevo B13: 14 -> 1
	Wait 2
	Off DO_09
	Jump Pallet(1, 1)
	Wait 2
	On DO_09

	Jump Pallet(1, 6) ' Huevo A14: 6 -> 10
	Wait 2
	Off DO_09
	Jump Pallet(1, 10)
	Wait 2
	On DO_09

	Jump Pallet(1, 1) ' Huevo B14: 1 -> 9
	Wait 2
	Off DO_09
	Jump Pallet(1, 9)
	Wait 2
	On DO_09

	Jump Pallet(1, 10) ' Huevo A15: 10 -> 2
	Wait 2
	Off DO_09
	Jump Pallet(1, 2)
	Wait 2
	On DO_09

	Jump Pallet(1, 9) ' Huevo B15: 9 -> 5
	Wait 2
	Off DO_09
	Jump Pallet(1, 5)
	Wait 2
	On DO_09

	Jump Pallet(1, 2) ' Huevo A16: 2 -> 15
	Wait 2
	Off DO_09
	Jump Pallet(1, 15)
	Wait 2
	On DO_09

	Jump Pallet(1, 5) ' Huevo B16: 5 -> 16
	Wait 2
	Off DO_09
	Jump Pallet(1, 16)
	Wait 2
	On DO_09

	Jump Pallet(1, 15) ' Huevo A17: 15 -> 28
	Wait 2
	Off DO_09
	Jump Pallet(1, 28)
	Wait 2
	On DO_09

	Jump Pallet(1, 16) ' Huevo B17: 16 -> 3
	Wait 2
	Off DO_09
	Jump Pallet(1, 3)
	Wait 2
	On DO_09

	Jump Pallet(1, 28) ' Huevo A18: 28 -> 24
	Wait 2
	Off DO_09
	Jump Pallet(1, 24)
	Wait 2
	On DO_09

	Jump Pallet(1, 3) ' Huevo B18: 3 -> 7
	Wait 2
	Off DO_09
	Jump Pallet(1, 7)
	Wait 2
	On DO_09

	Jump Pallet(1, 24) ' Huevo A19: 24 -> 11
	Wait 2
	Off DO_09
	Jump Pallet(1, 11)
	Wait 2
	On DO_09

	Jump Pallet(1, 7) ' Huevo B19: 7 -> 20
	Wait 2
	Off DO_09
	Jump Pallet(1, 20)
	Wait 2
	On DO_09

	Jump Pallet(1, 11) ' Huevo A20: 11 -> 3
	Wait 2
	Off DO_09
	Jump Pallet(1, 3)
	Wait 2
	On DO_09

	Jump Pallet(1, 20) ' Huevo B20: 20 -> 28
	Wait 2
	Off DO_09
	Jump Pallet(1, 28)
	Wait 2
	On DO_09

	Jump Pallet(1, 3) ' Huevo A21: 3 -> 7
	Wait 2
	Off DO_09
	Jump Pallet(1, 7)
	Wait 2
	On DO_09

	Jump Pallet(1, 28) ' Huevo B21: 28 -> 24
	Wait 2
	Off DO_09
	Jump Pallet(1, 24)
	Wait 2
	On DO_09

	Jump Pallet(1, 7) ' Huevo A22: 7 -> 20
	Wait 2
	Off DO_09
	Jump Pallet(1, 20)
	Wait 2
	On DO_09

	Jump Pallet(1, 24) ' Huevo B22: 24 -> 11
	Wait 2
	Off DO_09
	Jump Pallet(1, 11)
	Wait 2
	On DO_09

	Jump Pallet(1, 20) ' Huevo A23: 20 -> 16
	Wait 2
	Off DO_09
	Jump Pallet(1, 16)
	Wait 2
	On DO_09

	Jump Pallet(1, 11) ' Huevo B23: 11 -> 15
	Wait 2
	Off DO_09
	Jump Pallet(1, 15)
	Wait 2
	On DO_09

	Jump Pallet(1, 16) ' Huevo A24: 16 -> 27
	Wait 2
	Off DO_09
	Jump Pallet(1, 27)
	Wait 2
	On DO_09

	Jump Pallet(1, 15) ' Huevo B24: 15 -> 4
	Wait 2
	Off DO_09
	Jump Pallet(1, 4)
	Wait 2
	On DO_09

	Jump Pallet(1, 27) ' Huevo A25: 27 -> 23
	Wait 2
	Off DO_09
	Jump Pallet(1, 23)
	Wait 2
	On DO_09

	Jump Pallet(1, 4) ' Huevo B25: 4 -> 8
	Wait 2
	Off DO_09
	Jump Pallet(1, 8)
	Wait 2
	On DO_09

	Jump Pallet(1, 23) ' Huevo A26: 23 -> 12
	Wait 2
	Off DO_09
	Jump Pallet(1, 12)
	Wait 2
	On DO_09

	Jump Pallet(1, 8) ' Huevo B26: 8 -> 19
	Wait 2
	Off DO_09
	Jump Pallet(1, 19)
	Wait 2
	On DO_09

	Jump Pallet(1, 12) ' Huevo A27: 12 -> 4
	Wait 2
	Off DO_09
	Jump Pallet(1, 4)
	Wait 2
	On DO_09

	Jump Pallet(1, 19) ' Huevo B27: 19 -> 27
	Wait 2
	Off DO_09
	Jump Pallet(1, 27)
	Wait 2
	On DO_09

	Jump Pallet(1, 4) ' Huevo A28: 4 -> 8
	Wait 2
	Off DO_09
	Jump Pallet(1, 8)
	Wait 2
	On DO_09

	Jump Pallet(1, 27) ' Huevo B28: 27 -> 23
	Wait 2
	Off DO_09
	Jump Pallet(1, 23)
	Wait 2
	On DO_09

	Jump Pallet(1, 8) ' Huevo A29: 8 -> 19
	Wait 2
	Off DO_09
	Jump Pallet(1, 19)
	Wait 2
	On DO_09

	Jump Pallet(1, 23) ' Huevo B29: 23 -> 12
	Wait 2
	Off DO_09
	Jump Pallet(1, 12)
	Wait 2
	On DO_09

Fend
