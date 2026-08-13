
```python

Global Integer i

Function main
	Motor On
	Power High
	Accel 100, 100 '%
	Speed 100 '%

	Do
		Home
		Call Palletized
		Home
	Loop
Fend
Function Palletized
	Pallet 1, Origin, PointX, PointY, 6, 5
	Integer Verde(30)
	Integer Rosa(30)
	Verde(1) = 25
	Verde(2) = 21
	Verde(3) = 29
	Verde(4) = 18
	Verde(5) = 5
	Verde(6) = 9
	Verde(7) = 1
	Verde(8) = 14
	Verde(9) = 22
	Verde(10) = 30
	Verde(11) = 17
	Verde(12) = 6
	Verde(13) = 10
	Verde(14) = 2
	Verde(15) = 13
	Verde(16) = 26
	Verde(17) = 15
	Verde(18) = 28
	Verde(19) = 24
	Verde(20) = 11
	Verde(21) = 3
	Verde(22) = 7
	Verde(23) = 20
	Verde(24) = 16
	Verde(25) = 27
	Verde(26) = 19
	Verde(27) = 8
	Verde(28) = 4
	Verde(29) = 12
	Verde(30) = 23
	Rosa(1) = 6
	Rosa(2) = 10
	Rosa(3) = 2
	Rosa(4) = 13
	Rosa(5) = 26
	Rosa(6) = 22
	Rosa(7) = 30
	Rosa(8) = 17
	Rosa(9) = 9
	Rosa(10) = 1
	Rosa(11) = 14
	Rosa(12) = 25
	Rosa(13) = 21
	Rosa(14) = 29
	Rosa(15) = 18
	Rosa(16) = 5
	Rosa(17) = 16
	Rosa(18) = 3
	Rosa(19) = 7
	Rosa(20) = 20
	Rosa(21) = 28
	Rosa(22) = 24
	Rosa(23) = 11
	Rosa(24) = 15
	Rosa(25) = 4
	Rosa(26) = 12
	Rosa(27) = 23
	Rosa(28) = 27
	Rosa(29) = 19
	Rosa(30) = 8
	For i = 1 To 29
	
	    Jump Pallet(1, Verde(i))
	    Off DO_09
	    Jump Pallet(1, Verde(i + 1))
	    On DO_09
	
	    Jump Pallet(1, Rosa(i))
	    Off DO_09
	    Jump Pallet(1, Rosa(i + 1))
	    On DO_09
	
	Next
Fend
```
