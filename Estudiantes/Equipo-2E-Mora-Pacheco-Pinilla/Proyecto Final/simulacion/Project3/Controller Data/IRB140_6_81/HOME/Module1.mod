MODULE Module1
    !***********************************************************
    !
    ! Etapa 4 - Embalaje y envio por banda - ABB IRB 140 "Abel"
    ! Gripper SG90 + Arduino Nano v4.0
    !
    ! Señales fisicas del controlador:
    !   DI_01 = START            DO_01 = Lampara STANDBY
    !   DI_02 = STOP             DO_02 = Lampara RUN
    !   DI_03 = RESET            DO_03 = Lampara FAULT
    !   DI_04 = gripOK (Arduino) DO_04 = Gripper MSB -> Arduino
    !   DI_05 = HOME remoto      DO_05 = Gripper LSB -> Arduino
    !   DI_06 = START remoto     DO_06 = Falla -> Arduino
    !                            FWD_Conveyor / BWD_Conveyor
    !
    ! Gripper (DO_04, DO_05):
    !   00 = Abierto (10°)   - Reposo / Aproximacion
    !   10 = PCB (75°)       - Sujecion lateral PCB
    !   01 = Caja (45°)      - Sujecion lateral caja
    !   11 = Intermedio (30°)- Reservado
    !
    ! Maquina de estados: STANDBY -> RUN -> DONE -> STANDBY
    !                      FAULT -> STANDBY (por RESET)
    !
    ! Autor: Duvan Pacheco | Version: 4.0
    !
    !***********************************************************

    !--- ESTADOS ---
    CONST num EST_STANDBY := 0;
    CONST num EST_RUN := 1;
    CONST num EST_DONE := 2;
    CONST num EST_FAULT := 3;

    !--- TIEMPOS ---
    CONST num T_ESPERA_GRIP := 2;
    CONST num T_SONDEO := 0.5;
    CONST num T_CONVEYOR := 4.275;

    !--- HOME ---
    CONST jointtarget Home_ABS:= [[0,0,0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    !--- HERRAMIENTA ---
    PERS tooldata toolGripper:=[TRUE,[[5.679722831,0,128.679091982],[1,0,0,0]],[1,[0,0,1],[1,0,0,0],0,0,0]];

    !--- WORK OBJECTS ---
    PERS wobjdata wobj_Mesa:=[FALSE,TRUE,"",[[0,0,0],[1,0,0,0]],[[0,0,0],[1,0,0,0]]];
    PERS wobjdata wobj_Caja:=[FALSE,TRUE,"",[[0,0,0],[1,0,0,0]],[[0,0,0],[1,0,0,0]]];
    PERS wobjdata wobj_Banda:=[FALSE,TRUE,"",[[0,0,0],[1,0,0,0]],[[0,0,0],[1,0,0,0]]];

    !--- VARIABLES ---
    VAR num nEstado := 0;
    VAR num nPiezas := 0;
    PERS num nPiezasTot := 0;
    VAR bool bTimeout := FALSE;
    VAR num nComandoGripper := 0;

    !--- ROBTARGETS: Waypoints generales ---
    CONST robtarget Target_AproxMesa:=
        [[0,0,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    !--- ROBTARGETS: PCB 1 ---
    CONST robtarget pPCB1_Approach1:=
        [[0,0,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget pPCB1_Approach2:=
        [[0,0,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget pPCB1Grab:=
        [[0,0,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    !--- ROBTARGETS: PCB 2 ---
    CONST robtarget pPCB2_Approach1:=
        [[0,0,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget pPCB2_Approach2:=
        [[0,0,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget pPCB2Grab:=
        [[0,0,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    !--- ROBTARGETS: Caja 1 ---
    CONST robtarget pBox1_Approach:=
        [[0,0,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget pBox1_Place:=
        [[0,0,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget pBox1_ApproachSide:=
        [[0,0,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget pBox1_Grab:=
        [[0,0,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    !--- ROBTARGETS: Caja 2 ---
    CONST robtarget pBox2_Approach:=
        [[0,0,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget pBox2_Place:=
        [[0,0,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget pBox2_ApproachSide:=
        [[0,0,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget pBox2_Grab:=
        [[0,0,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    !--- ROBTARGETS: Banda ---
    CONST robtarget pConv_Approach:=
        [[0,0,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget pConv_Place:=
        [[0,0,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    !===========================================================
    ! BUCLE PRINCIPAL
    !===========================================================
    PROC main()
        Inicializar;
        WHILE TRUE DO
            PublicarEstado EST_STANDBY;
            EsperarOrden;
        ENDWHILE
    ENDPROC

    !===========================================================
    ! INICIALIZACION
    !===========================================================
    PROC Inicializar()
        TPErase;
        TPWrite "========================================";
        TPWrite " ETAPA 4 - EMBALAJE Y ENVIO POR BANDA ";
        TPWrite " ABB IRB 140 - ABEL  |  v4.0           ";
        TPWrite "========================================";

        PublicarEstado EST_FAULT;
        AbrirGripper;
        IrAHome;
        nPiezas := 0;
        Reset FWD_Conveyor;
        Reset BWD_Conveyor;
        TPWrite "ETAPA 4 LISTA. PRESIONE START.";
        PublicarEstado EST_STANDBY;
    ENDPROC

    !===========================================================
    ! ESPERA DE ORDENES
    !===========================================================
    PROC EsperarOrden()
        WHILE TRUE DO
            IF OrdenHome() THEN
                EsperarLiberacion;
                IrAHome;
                PublicarEstado EST_STANDBY;
            ENDIF
            IF OrdenStart() THEN
                EsperarLiberacion;
                PublicarEstado EST_RUN;
                CicloEtapa4;
                RETURN;
            ENDIF
            WaitTime T_SONDEO;
        ENDWHILE
    ENDPROC

    !===========================================================
    ! CICLO ETAPA 4 - 2 PCBs + 2 CAJAS
    !
    ! Agarre lateral con secuencia:
    !   Waypoint -> Approach1 -> Approach2 -> Grab (lineal)
    !   -> cerrar -> Approach2 -> Approach1 -> Waypoint
    !===========================================================
    PROC CicloEtapa4()
        TPWrite "========================================";
        TPWrite " CICLO DE EMBALAJE INICIADO (2 PCBs)";
        TPWrite "========================================";

        ! ============ PCB 1 + CAJA 1 ============
        TPWrite "--- PROCESANDO PCB 1 ---";

        ! 1. Pick PCB 1
        AbrirGripper;
        MoveJ Target_AproxMesa,v300,z50,toolGripper\WObj:=wobj_Mesa;
        MoveJ pPCB1_Approach1,v200,z50,toolGripper\WObj:=wobj_Mesa;
        MoveJ pPCB1_Approach2,v100,z30,toolGripper\WObj:=wobj_Mesa;
        MoveL pPCB1Grab,v50,fine,toolGripper\WObj:=wobj_Mesa;
        CerrarSobrePCB;
        MoveL pPCB1_Approach2,v100,z30,toolGripper\WObj:=wobj_Mesa;
        MoveJ pPCB1_Approach1,v200,z50,toolGripper\WObj:=wobj_Mesa;
        MoveJ Target_AproxMesa,v300,z50,toolGripper\WObj:=wobj_Mesa;
        TPWrite "    PCB 1 TOMADA";
        VerificarParada;

        ! 2. Depositar PCB 1 en caja 1
        MoveJ pBox1_Approach,v200,z50,toolGripper\WObj:=wobj_Caja;
        MoveL pBox1_Place,v50,fine,toolGripper\WObj:=wobj_Caja;
        AbrirGripper;
        MoveL pBox1_Approach,v100,z50,toolGripper\WObj:=wobj_Caja;
        TPWrite "    PCB 1 DEPOSITADA EN CAJA 1";
        VerificarParada;

        ! 3. Pick caja 1 (agarre lateral)
        AbrirGripper;
        MoveJ pBox1_ApproachSide,v200,z50,toolGripper\WObj:=wobj_Caja;
        MoveL pBox1_Grab,v50,fine,toolGripper\WObj:=wobj_Caja;
        CerrarSobreCaja;
        MoveL pBox1_ApproachSide,v100,z50,toolGripper\WObj:=wobj_Caja;
        TPWrite "    CAJA 1 TOMADA";
        VerificarParada;

        ! 4. Colocar paquete 1 en banda
        Reset FWD_Conveyor;
        MoveJ pConv_Approach,v200,z50,toolGripper\WObj:=wobj_Banda;
        MoveL pConv_Place,v50,fine,toolGripper\WObj:=wobj_Banda;
        AbrirGripper;
        MoveL pConv_Approach,v100,z50,toolGripper\WObj:=wobj_Banda;
        TPWrite "    PAQUETE 1 EN BANDA";
        VerificarParada;

        ! 5. Enviar paquete 1 por banda
        Set FWD_Conveyor;
        WaitTime T_CONVEYOR;
        Reset FWD_Conveyor;
        TPWrite "    PAQUETE 1 ENVIADO";

        ! ============ PCB 2 + CAJA 2 ============
        TPWrite "--- PROCESANDO PCB 2 ---";

        ! 1. Pick PCB 2
        AbrirGripper;
        MoveJ Target_AproxMesa,v300,z50,toolGripper\WObj:=wobj_Mesa;
        MoveJ pPCB2_Approach1,v200,z50,toolGripper\WObj:=wobj_Mesa;
        MoveJ pPCB2_Approach2,v100,z30,toolGripper\WObj:=wobj_Mesa;
        MoveL pPCB2Grab,v50,fine,toolGripper\WObj:=wobj_Mesa;
        CerrarSobrePCB;
        MoveL pPCB2_Approach2,v100,z30,toolGripper\WObj:=wobj_Mesa;
        MoveJ pPCB2_Approach1,v200,z50,toolGripper\WObj:=wobj_Mesa;
        MoveJ Target_AproxMesa,v300,z50,toolGripper\WObj:=wobj_Mesa;
        TPWrite "    PCB 2 TOMADA";
        VerificarParada;

        ! 2. Depositar PCB 2 en caja 2
        MoveJ pBox2_Approach,v200,z50,toolGripper\WObj:=wobj_Caja;
        MoveL pBox2_Place,v50,fine,toolGripper\WObj:=wobj_Caja;
        AbrirGripper;
        MoveL pBox2_Approach,v100,z50,toolGripper\WObj:=wobj_Caja;
        TPWrite "    PCB 2 DEPOSITADA EN CAJA 2";
        VerificarParada;

        ! 3. Pick caja 2 (agarre lateral)
        AbrirGripper;
        MoveJ pBox2_ApproachSide,v200,z50,toolGripper\WObj:=wobj_Caja;
        MoveL pBox2_Grab,v50,fine,toolGripper\WObj:=wobj_Caja;
        CerrarSobreCaja;
        MoveL pBox2_ApproachSide,v100,z50,toolGripper\WObj:=wobj_Caja;
        TPWrite "    CAJA 2 TOMADA";
        VerificarParada;

        ! 4. Colocar paquete 2 en banda
        Reset FWD_Conveyor;
        MoveJ pConv_Approach,v200,z50,toolGripper\WObj:=wobj_Banda;
        MoveL pConv_Place,v50,fine,toolGripper\WObj:=wobj_Banda;
        AbrirGripper;
        MoveL pConv_Approach,v100,z50,toolGripper\WObj:=wobj_Banda;
        TPWrite "    PAQUETE 2 EN BANDA";
        VerificarParada;

        ! 5. Enviar paquete 2 por banda
        Set FWD_Conveyor;
        WaitTime T_CONVEYOR;
        Reset FWD_Conveyor;
        TPWrite "    PAQUETE 2 ENVIADO";

        ! --- FIN ---
        SenalarDone;
    ENDPROC

    !===========================================================
    ! PUBLICAR ESTADO EN LAMPARAS + BIT DE FALLA
    !===========================================================
    PROC PublicarEstado(num nNuevo)
        TEST nNuevo
        CASE EST_STANDBY:
            SetDO DO_01, 1;
            SetDO DO_02, 0;
            SetDO DO_03, 0;
            SetDO DO_06, 0;
        CASE EST_RUN:
            SetDO DO_01, 0;
            SetDO DO_02, 1;
            SetDO DO_03, 0;
            SetDO DO_06, 0;
        CASE EST_DONE:
            SetDO DO_01, 0;
            SetDO DO_02, 0;
            SetDO DO_03, 0;
            SetDO DO_06, 0;
        CASE EST_FAULT:
            SetDO DO_01, 0;
            SetDO DO_02, 0;
            SetDO DO_03, 1;
            SetDO DO_06, 1;
        DEFAULT:
            SetDO DO_01, 0;
            SetDO DO_02, 0;
            SetDO DO_03, 1;
            SetDO DO_06, 1;
        ENDTEST
        nEstado := nNuevo;
    ENDPROC

    !===========================================================
    ! SENALIZACION DONE (parpadeo DO_01 2Hz durante 2s)
    !===========================================================
    PROC SenalarDone()
        VAR num i;
        PublicarEstado EST_DONE;
        Incr nPiezas;
        nPiezasTot := nPiezasTot + 1;
        TPWrite "========================================";
        TPWrite " PCB EMPACADA Y ENVIADA";
        TPWrite " CONTADOR: " + NumToStr(nPiezas,0);
        TPWrite " TOTAL ACUMULADO: " + NumToStr(nPiezasTot,0);
        TPWrite "========================================";

        FOR i FROM 1 TO 4 DO
            SetDO DO_01, 1;
            WaitTime 0.25;
            SetDO DO_01, 0;
            WaitTime 0.25;
        ENDFOR
        PublicarEstado EST_STANDBY;
    ENDPROC

    !===========================================================
    ! FUNCIONES DE ORDENES (botonera + comandos remotos)
    !===========================================================
    FUNC bool OrdenStart()
        RETURN DI_01 = 1 OR DI_06 = 1;
    ENDFUNC

    FUNC bool OrdenHome()
        RETURN DI_05 = 1;
    ENDFUNC

    FUNC bool OrdenStop()
        RETURN DI_02 = 1;
    ENDFUNC

    FUNC bool OrdenReset()
        RETURN DI_03 = 1;
    ENDFUNC

    PROC EsperarLiberacion()
        WHILE OrdenStart() OR OrdenHome() OR OrdenReset() DO
            WaitTime T_SONDEO;
        ENDWHILE
    ENDPROC

    !===========================================================
    ! VERIFICACION DE PARADA ENTRE MOVIMIENTOS
    !===========================================================
    PROC VerificarParada()
        IF OrdenStop() THEN
            TPWrite "PARADA SOLICITADA POR EL OPERADOR";
            IF nComandoGripper = 0 THEN
                AbrirGripper;
            ENDIF
            IrAHome;
            PublicarEstado EST_STANDBY;
            Stop;
        ENDIF
    ENDPROC

    !===========================================================
    ! CONTROL DEL GRIPPER (con WaitDI DI_04)
    !
    !   DO_04 DO_05 | Comando   | Angulo | Aplicacion
    !   ------ ------|-----------|--------|-----------
    !     0     0    | Abierto   | 10°    | Reposo / Aprox
    !     1     0    | Cierre PCB| 75°    | Sujecion lateral PCB
    !     0     1    | Caja      | 45°    | Sujecion lateral caja
    !     1     1    | Intermedio| 30°    | Reservado
    !===========================================================
    PROC AbrirGripper()
        SetDO DO_04, 0;
        SetDO DO_05, 0;
        nComandoGripper := 0;
        WaitDI DI_04, 1 \MaxTime:=T_ESPERA_GRIP \TimeFlag:=bTimeout;
        IF bTimeout THEN
            DeclararFalla "El gripper no confirmo la apertura";
        ENDIF
    ENDPROC

    PROC CerrarSobrePCB()
        SetDO DO_04, 1;
        SetDO DO_05, 0;
        nComandoGripper := 2;
        WaitDI DI_04, 1 \MaxTime:=T_ESPERA_GRIP \TimeFlag:=bTimeout;
        IF bTimeout THEN
            DeclararFalla "Fallo de sujecion sobre la PCB";
        ENDIF
    ENDPROC

    PROC CerrarSobreCaja()
        SetDO DO_04, 0;
        SetDO DO_05, 1;
        nComandoGripper := 1;
        WaitDI DI_04, 1 \MaxTime:=T_ESPERA_GRIP \TimeFlag:=bTimeout;
        IF bTimeout THEN
            DeclararFalla "Fallo de sujecion sobre la caja de empaque";
        ENDIF
    ENDPROC

    !===========================================================
    ! TRATAMIENTO DE FALLAS
    !===========================================================
    PROC DeclararFalla(string sCausa)
        PublicarEstado EST_FAULT;
        TPWrite "========================================";
        TPWrite " FALLA: " + sCausa;
        TPWrite " CORRIJA LA CAUSA Y PULSE RESET (NEGRO)";
        TPWrite "========================================";

        WHILE NOT OrdenReset() DO
            WaitTime T_SONDEO;
        ENDWHILE
        EsperarLiberacion;

        AbrirGripper;
        IrAHome;
        PublicarEstado EST_STANDBY;
        Stop;
    ENDPROC

    !===========================================================
    ! IR A HOME
    !===========================================================
    PROC IrAHome()
        AbrirGripper;
        MoveAbsJ Home_ABS, v300, z1, toolGripper;
        TPWrite "ROBOT EN HOME";
    ENDPROC

ENDMODULE