Global Integer i

Global Integer huevo_uno(29, 1)
Global Integer huevo_dos(29, 1)
Global Integer turno(0, 1)


Function main

' Huevo 1: inicia en (1,1)

huevo_uno(0, 0) = 1; huevo_uno(0, 1) = 1;
huevo_uno(1, 0) = 2;   huevo_uno(1, 1) = 3;
huevo_uno(2, 0) = 1;   huevo_uno(2, 1) = 5;
huevo_uno(3, 0) = 3;   huevo_uno(3, 1) = 4;
huevo_uno(4, 0) = 5;   huevo_uno(4, 1) = 5;
huevo_uno(5, 0) = 6;   huevo_uno(5, 1) = 3;
huevo_uno(6, 0) = 5;   huevo_uno(6, 1) = 1;
huevo_uno(7, 0) = 3;   huevo_uno(7, 1) = 2;
huevo_uno(8, 0) = 1;   huevo_uno(8, 1) = 3;
huevo_uno(9, 0) = 2;   huevo_uno(9, 1) = 1;
huevo_uno(10, 0) = 4;  huevo_uno(10, 1) = 2;
huevo_uno(11, 0) = 6;  huevo_uno(11, 1) = 1;
huevo_uno(12, 0) = 5;  huevo_uno(12, 1) = 3;
huevo_uno(13, 0) = 6;  huevo_uno(13, 1) = 5;
huevo_uno(14, 0) = 4;  huevo_uno(14, 1) = 4;
huevo_uno(15, 0) = 2;  huevo_uno(15, 1) = 5;
huevo_uno(16, 0) = 3;  huevo_uno(16, 1) = 3;
huevo_uno(17, 0) = 1;  huevo_uno(17, 1) = 2;
huevo_uno(18, 0) = 2;  huevo_uno(18, 1) = 4;
huevo_uno(19, 0) = 4;  huevo_uno(19, 1) = 5;
huevo_uno(20, 0) = 6;  huevo_uno(20, 1) = 4;
huevo_uno(21, 0) = 5;  huevo_uno(21, 1) = 2;
huevo_uno(22, 0) = 3;  huevo_uno(22, 1) = 1;
huevo_uno(23, 0) = 4;  huevo_uno(23, 1) = 3;
huevo_uno(24, 0) = 2;  huevo_uno(24, 1) = 2;
huevo_uno(25, 0) = 1;  huevo_uno(25, 1) = 4;
huevo_uno(26, 0) = 3;  huevo_uno(26, 1) = 5;
huevo_uno(27, 0) = 5;  huevo_uno(27, 1) = 4;
huevo_uno(28, 0) = 6;  huevo_uno(28, 1) = 2;
huevo_uno(29, 0) = 4;  huevo_uno(29, 1) = 1;

' Huevo 2: inicia en el extremo opuesto
huevo_dos(0, 0) = 6;   huevo_dos(0, 1) = 5;
huevo_dos(1, 0) = 4;   huevo_dos(1, 1) = 4;
huevo_dos(2, 0) = 2;   huevo_dos(2, 1) = 5;
huevo_dos(3, 0) = 1;   huevo_dos(3, 1) = 3;
huevo_dos(4, 0) = 2;   huevo_dos(4, 1) = 1;
huevo_dos(5, 0) = 4;   huevo_dos(5, 1) = 2;
huevo_dos(6, 0) = 6;   huevo_dos(6, 1) = 1;
huevo_dos(7, 0) = 5;   huevo_dos(7, 1) = 3;
huevo_dos(8, 0) = 3;   huevo_dos(8, 1) = 2;
huevo_dos(9, 0) = 1;   huevo_dos(9, 1) = 1;
huevo_dos(10, 0) = 2;  huevo_dos(10, 1) = 3;
huevo_dos(11, 0) = 1;  huevo_dos(11, 1) = 5;
huevo_dos(12, 0) = 3;  huevo_dos(12, 1) = 4;
huevo_dos(13, 0) = 5;  huevo_dos(13, 1) = 5;
huevo_dos(14, 0) = 6;  huevo_dos(14, 1) = 3;
huevo_dos(15, 0) = 5;  huevo_dos(15, 1) = 1;
huevo_dos(16, 0) = 4;  huevo_dos(16, 1) = 3;
huevo_dos(17, 0) = 2;  huevo_dos(17, 1) = 2;
huevo_dos(18, 0) = 1;  huevo_dos(18, 1) = 4;
huevo_dos(19, 0) = 3;  huevo_dos(19, 1) = 5;
huevo_dos(20, 0) = 5;  huevo_dos(20, 1) = 4;
huevo_dos(21, 0) = 6;  huevo_dos(21, 1) = 2;
huevo_dos(22, 0) = 4;  huevo_dos(22, 1) = 1;
huevo_dos(23, 0) = 3;  huevo_dos(23, 1) = 3;
huevo_dos(24, 0) = 1;  huevo_dos(24, 1) = 2;
huevo_dos(25, 0) = 2;  huevo_dos(25, 1) = 4;
huevo_dos(26, 0) = 4;  huevo_dos(26, 1) = 5;
huevo_dos(27, 0) = 6;  huevo_dos(27, 1) = 4;
huevo_dos(28, 0) = 5;  huevo_dos(28, 1) = 2;
huevo_dos(29, 0) = 3;  huevo_dos(29, 1) = 1;

    Motor On
        Power High
        Accel 100, 100 '%
        Speed 100 '%
        Home
        Call Palletized
        Home
Fend
Function Palletized
    Pallet 1, Origin, Puntox, Puntoy, 6, 5
    For i = 0 To 28
        Print "Ciclo número:", i
        Jump Pallet(1, huevo_uno(i, 0), huevo_uno(i, 1))
        Off DO_09
        Wait 0.5
        Jump Pallet(1, huevo_uno(i + 1, 0), huevo_uno(i + 1, 1))
        On DO_09
        Wait 0.5
        Jump Pallet(1, huevo_dos(i, 0), huevo_dos(i, 1))
        Off DO_09
        Wait 0.5
        Jump Pallet(1, huevo_dos(i + 1, 0), huevo_dos(i + 1, 1))
        On DO_09
        Wait 0.5
    Next
Fend