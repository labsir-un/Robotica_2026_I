MODULE Module1

!===========================================================
! HERRAMIENTA Y OBJETOS DE TRABAJO
!===========================================================
PERS tooldata toolGripper:=[TRUE,[[5.679722754,2.287280651,120.075445417],[1,0,0,0]],[1,[0,0,1],[1,0,0,0],0,0,0]];
PERS wobjdata wobj_Mesa:=[FALSE,TRUE,"",[[0,0,0],[1,0,0,0]],[[0,0,0],[1,0,0,0]]];
PERS wobjdata wobj_Banda:=[FALSE,TRUE,"",[[0,0,0],[1,0,0,0]],[[0,0,0],[1,0,0,0]]];

!===========================================================
! POSICION DE REPOSO
!===========================================================
CONST jointtarget Home_ABS:=[[0,0,0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

!===========================================================
! TARGETS (Z incrementado en +60 mm)
!===========================================================
CONST robtarget pPCB1_Approach:=[[96,-439,425],[0,0,1,0],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
CONST robtarget pPCB1Grab:=[[96,-439,345],[0,0,1,0],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
CONST robtarget pPCB2_Approach:=[[96,-549,425],[0,0,1,0],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
CONST robtarget pPCB2Grab:=[[96,-549,345],[0,0,1,0],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

CONST robtarget pCajaApproach:=[[582,63.5,488],[0,0,1,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
CONST robtarget pCajaPlace:=[[582,63.5,158],[0,0,1,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST num T_SONDEO:=2;
    CONST num T_RETROCESO:=5;
    CONST num T_PASO:=5;
    CONST num T_AVANCE_CAJA:=5;
!===========================================================
! BUCLE PRINCIPAL
!===========================================================
PROC main()
    ! Configuraciones iniciales basicas
    ConfL \On;
    ConfJ \On;
    SingArea \Off;
    
    Reset FWD_Conveyor;
    
    IrAHome;
    TPWrite "Sistema Listo.";
    TPWrite "- DI01 para iniciar ciclo directo";
    TPWrite "- DI02 para calibrar banda (5 seg)";

    WHILE TRUE DO
        IF DI_01 = 1 THEN
            CicloProduccion;
        ELSEIF DI_02 = 1 THEN
            ModoCalibracion;
        ENDIF
        
        WaitTime 0.2; ! Pausa ligera para no saturar el controlador
    ENDWHILE
ENDPROC

!===========================================================
! MODO CALIBRACION (DI_02)
!===========================================================
PROC ModoCalibracion()
    TPWrite "Calibrando... Avanzando banda 5s";
    
    Set FWD_Conveyor;
    WaitTime 3.8;
    Reset FWD_Conveyor;
    
    TPWrite "Calibracion finalizada. Caja en marca inicial.";
    
    ! Espera a que se suelte el boton para evitar ciclos infinitos
    WaitUntil DI_02 = 0;
ENDPROC

!===========================================================
! CICLO DE PRODUCCION NORMAL (DI_01)
!===========================================================
PROC CicloProduccion()
    TPWrite "Iniciando ciclo de produccion...";

    ! 1. Avanzar la banda: trae la CAJA 1 al robot
    Set FWD_Conveyor;
    WaitTime T_AVANCE_CAJA;
    Reset FWD_Conveyor;

    ! 2. Tomar y depositar PCB 1 en la CAJA 1
    TomarPCB 1;
    DepositarEnCaja;

    ! 3. Avanzar la banda otra vez: saca la CAJA 1 y trae la CAJA 2
    Set FWD_Conveyor;
    WaitTime T_AVANCE_CAJA;
    Reset FWD_Conveyor;

    ! 4. Tomar y depositar PCB 2 en la CAJA 2
    TomarPCB 2;
    DepositarEnCaja;

    ! 5. Expulsar la tanda final
    Set FWD_Conveyor;
    WaitTime 6;
    Reset FWD_Conveyor;

    IrAHome;
    TPWrite "Ciclo terminado. Esperando nueva orden.";

    WaitUntil DI_01 = 0;
ENDPROC
!===========================================================
! RUTINAS DE MOVIMIENTO Y CONTROL
!===========================================================
PROC TomarPCB(num nPCB)
    AbrirGripper;

    IF nPCB = 1 THEN
        MoveJ pPCB1_Approach,v300,z20,toolGripper\WObj:=wobj_Mesa;
        MoveL pPCB1Grab,v50,fine,toolGripper\WObj:=wobj_Mesa;
        CerrarGripper;
        MoveL pPCB1_Approach,v100,z20,toolGripper\WObj:=wobj_Mesa;
    ELSE
        MoveJ pPCB2_Approach,v300,z20,toolGripper\WObj:=wobj_Mesa;
        MoveL pPCB2Grab,v50,fine,toolGripper\WObj:=wobj_Mesa;
        CerrarGripper;
        MoveL pPCB2_Approach,v100,z20,toolGripper\WObj:=wobj_Mesa;
    ENDIF
ENDPROC

PROC DepositarEnCaja()
    MoveJ pCajaApproach,v300,z10,toolGripper\WObj:=wobj_Banda;
    MoveL pCajaPlace,v50,fine,toolGripper\WObj:=wobj_Banda;
    AbrirGripper;
    MoveL pCajaApproach,v100,fine,toolGripper\WObj:=wobj_Banda;
ENDPROC

PROC AbrirGripper()
    SetDO DO_04, 0;
    WaitTime 1; ! Tiempo de espera en lugar de validacion de sensor
ENDPROC

PROC CerrarGripper()
    SetDO DO_04, 1;
    WaitTime 1; ! Tiempo de espera en lugar de validacion de sensor
ENDPROC

PROC IrAHome()
    AbrirGripper;
    MoveAbsJ Home_ABS, v300, fine, toolGripper;
ENDPROC
    PROC EsperarOrden()
        EsperarLiberacion;
        IrAHome;
        EsperarLiberacion;
        IrAHome;
        CalibrarBanda;
        EsperarLiberacion;
        CicloEtapa4;
        WaitTime T_SONDEO;
    ENDPROC
    PROC CicloEtapa4()
        EsperarConfirmacion;
        PosicionarCaja;
        VerificarParada;
        VerificarParada;
        DepositarEnCaja;
        VerificarParada;
        IrAHome;
        SenalarDone;
    ENDPROC
    PROC SenalarDone()
        SetDO DO_01,1;
        WaitTime 0.25;
        SetDO DO_01,0;
        WaitTime 0.25;
    ENDPROC
    PROC EsperarLiberacion()
        WaitTime T_SONDEO;
    ENDPROC
    PROC VerificarParada()
        Reset FWD_Conveyor;
        Reset BWD_Conveyor;
        IrAHome;
        IrAHome;
        AbrirGripper;
    ENDPROC
    PROC CerrarSobrePCB()
        SetDO DO_04,1;
    ENDPROC
    PROC CerrarSobreCaja()
        SetDO DO_04,0;
        SetDO DO_05,1;
    ENDPROC
    PROC Inicializar()
        ConfL\On;
        ConfJ\On;
        SingArea\Off;
        AbrirGripper;
        IrAHome;
        Reset FWD_Conveyor;
        Reset BWD_Conveyor;
        CalibrarBanda;
    ENDPROC
    PROC CalibrarBanda()
        Reset FWD_Conveyor;
        Reset BWD_Conveyor;
        EsperarConfirmacion;
        Reset FWD_Conveyor;
        Set BWD_Conveyor;
        WaitTime T_RETROCESO;
        Reset BWD_Conveyor;
        EsperarConfirmacion;
    ENDPROC
    PROC PosicionarCaja()
        Reset BWD_Conveyor;
        Set FWD_Conveyor;
        WaitTime T_PASO;
        Reset FWD_Conveyor;
    ENDPROC
    PROC EsperarConfirmacion()
        EsperarLiberacion;
        Set FWD_Conveyor;
        EsperarLiberacion;
    ENDPROC

ENDMODULE