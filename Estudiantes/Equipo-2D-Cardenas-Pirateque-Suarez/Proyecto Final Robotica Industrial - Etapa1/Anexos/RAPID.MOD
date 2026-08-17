MODULE Module1

    !====================================
    ! VARIABLES
    !====================================

    CONST robtarget Target_36:=[[30,30,-50],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_35:=[[30,30,-798.16],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_30:=[[30.000146555,30.000033692,-11.381966907],[0.996910434,0.002545816,-0.069559583,0.036394646],[-2,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_39:=[[357.5,525,-326.5],[1,0,0,0],[0,-2,1,1],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_40:=[[351.805611266,539.737050867,-72.236355663],[0.981583241,-0.078929784,0.167027936,-0.048642561],[0,-2,1,1],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_49:=[[357.5,305,-326.5],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_50:=[[357.5,305,-50],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_59:=[[357.5,85,-326.5],[1,0,0,0],[0,0,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_60:=[[357.5,85,-50],[1,0,0,0],[0,0,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_69:=[[200,305,-326.5],[1,0,0,0],[0,1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_70:=[[200,305,-50],[1,0,0,0],[0,1,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS tooldata MyNewToolEI:=[TRUE,[[0.05,0,41.6],[1,0,0,0]],[1,[0,0,1],[1,0,0,0],0,0,0]];
    TASK PERS wobjdata Workobject_9:=[FALSE,TRUE,"",[[340.64,-9.06,-420.092],[1,0,0,0]],[[-410,-593.41,264],[0,0.707106781,0.707106781,0]]];
    TASK PERS wobjdata Workobject_13:=[FALSE,TRUE,"",[[50,0,-404],[1,0,0,0]],[[600,721,702],[0,-0.707106781,0.707106781,0]]];
    CONST robtarget Target_Home:=[[542.293308043,0,658.65669873],[0.5,0,0.866025404,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! Contadores
    PERS num ContRes:=0;
    PERS num ContCap:=0;
    PERS num ContCon:=0;
    PERS num ContCI:=0;
    PERS num Total:=0;

    ! Estado del proceso
    PERS num Estado:=0;
    ! 0=Parado
    ! 1=Recepción
    ! 2=Clasificación
    ! 3=Ordenamiento
    ! 4=Finalizado

    ! Tipo detectado
    PERS num Tipo:=0;
    ! 0=Ninguno
    ! 1=Resistencia
    ! 2=Capacitor
    ! 3=Conector
    ! 4=CI

    ! Variables HMI
    PERS bool BtnInicio:=FALSE;
    PERS bool BtnReset:=FALSE;

    PERS num ConfirmarClasificacion:=0;
    !0 Esperando
    !1 SI
    !2 NO
    !3 DESCARTAR

    PERS num ConfirmarPick:=0;
    !0 Esperando
    !1 SI
    !2 NO
    !3 DESCARTAR

    PERS num ConfirmarPlace:=0;
    !0 Esperando
    !1 SI
    !2 NO
    PERS bool PlaceOK:=FALSE;

    PERS num Progreso:=0;

    PERS string MensajeEstado:="Almacenando resistencia";

    PERS num FIN:=0;
    
    PERS num Ninguno:=0;
    
    

    VAR intnum IntSalida;

    !====================================
    PROC main()

        CONNECT IntSalida WITH RevisarEmergencia;

        ISignalDO DO_01,1,IntSalida;

        WHILE TRUE DO

            InicializarSistema;

            EsperarInicio;

            WHILE Total<2 DO

                EsperarComponente;

                CapturarImagen;

                ClasificarComponente;

                ConfirmarClasificacionProc;

                RealizarPick;

                Realizaraproxpick;

                ConfirmarPickProc;

                RealizarPlace;

                ConfirmarPlaceProc;

                IF PlaceOK THEN

                    ActualizarInventario;

                ENDIF

            ENDWHILE

            FinEtapa;

        ENDWHILE

    ENDPROC

    PROC InicializarSistema()

        !Reiniciar variables

        MensajeEstado:="Inicialización ...";
        
        WaitTime 2;

        ContRes:=0;

        ContCap:=0;

        ContCon:=0;

        ContCI:=0;

        Total:=0;

        FIN:=0;
        
        Ninguno:=0;

        Estado:=0;

        Tipo:=0;

        Progreso:=0;

        ! Reiniciar botones HMI

        BtnInicio:=FALSE;

        BtnReset:=FALSE;

        ConfirmarClasificacion:=0;

        PlaceOK:=FALSE;

        ConfirmarPick:=0;

        ConfirmarPlace:=0;

        ! Apagar salidas

        Reset DO_01;
        Reset DO_05;
        Set DO_06;

        Reset FWD_Conveyor;
        Reset BWD_Conveyor;

        ! Ir HOME

        Path_10;

    ENDPROC

    PROC EsperarInicio()

        Estado:=0;

        MensajeEstado:="Esperando Inicio";

        WaitUntil BtnInicio;

        BtnInicio:=FALSE;

    ENDPROC

    TRAP RevisarEmergencia


        MensajeEstado:="PARADA DE SOFTWARE, oprima inicio para continuar";

        !-------------------------
        ! Apagar actuadores
        !-------------------------
        Reset DO_01;
        Reset DO_05;
        Set DO_06;
        ! Electroimán

        Reset FWD_Conveyor;
        Reset BWD_Conveyor;

        !-------------------------
        ! Estado HMI
        !-------------------------

        Estado:=99;

        !-------------------------
        ! Esperar reinicio
        !-------------------------

        WaitUntil BtnInicio;

        BtnInicio:=FALSE;

        MensajeEstado:="Reanudando proceso";


    ENDTRAP

    PROC EsperarComponente()

        Estado:=1;

        MensajeEstado:="Esperando componente";

        ! Encender banda

        Set FWD_Conveyor;
        Set BWD_Conveyor;

        WaitDI DI_04,1;

        ! Detener banda

        Reset FWD_Conveyor;
        Reset BWD_Conveyor;

    ENDPROC

    PROC CapturarImagen()

        Estado:=2;

        MensajeEstado:="Capturando imagen";

        WaitTime 3;

        PulseDO DO_05;

        WaitTime 5;

    ENDPROC

    PROC ClasificarComponente()

        Estado:=2;
        
        IF DI_07=0 AND DI_08=0 AND DI_09=0 AND DI_10=0 THEN

            Tipo:=0;
            
            Ninguno:=1;

            MensajeEstado:="Tipo: No identificado";

        ENDIF

        IF DI_07=1 THEN

            Tipo:=1;

            MensajeEstado:="Tipo: Resistencia";

        ENDIF

        IF DI_08=1 THEN

            Tipo:=2;

            MensajeEstado:="Tipo: Capacitor";

        ENDIF

        IF DI_09=1 THEN

            Tipo:=3;

            MensajeEstado:="Tipo: Conector";

        ENDIF

        IF DI_10=1 THEN

            Tipo:=4;

            MensajeEstado:="Tipo: Circuito integrado";

        ENDIF

        WaitTime 3;

    ENDPROC

    PROC ConfirmarClasificacionProc()

        MensajeEstado:="Esperando confirmación de selección";

        WaitUntil ConfirmarClasificacion<>0;

        TEST ConfirmarClasificacion

        CASE 1:

            ! Todo bien

            Set FWD_Conveyor;
            Set BWD_Conveyor;

            WaitTime 1.4;

            Reset FWD_Conveyor;
            Reset BWD_Conveyor;

        CASE 2:
            
            Ninguno:=0;
            
            ConfirmarClasificacion:=0;

            Set BWD_Conveyor;

            WaitTime 1.5;

            Reset BWD_Conveyor;

            EsperarComponente;

            CapturarImagen;

            ClasificarComponente;

            ConfirmarClasificacionProc;

        CASE 3:
        
            Ninguno:=0;

            ConfirmarClasificacion:=0;

            EsperarComponente;

            CapturarImagen;

            ClasificarComponente;

            ConfirmarClasificacionProc;

        ENDTEST

        ConfirmarClasificacion:=0;

    ENDPROC

    PROC RealizarPick()

        Estado:=3;

        MensajeEstado:="Realizando PICK";

        Path_11;

        Reset DO_06;

    ENDPROC

    PROC Realizaraproxpick()

        Estado:=3;

        Path_11_1;

    ENDPROC

    PROC ConfirmarPickProc()

        MensajeEstado:="Esperando confirmación de PICK";

        WaitUntil ConfirmarPick<>0;

        TEST ConfirmarPick

        CASE 1:

            ! Todo bien

            MensajeEstado:="PICK confirmado";

        CASE 2:

            ConfirmarPick:=0;
        
            MensajeEstado:="Reintentando PICK";

            Realizaraproxpick;

            ConfirmarPickProc;

        CASE 3:

            ConfirmarPick:=0;
        
            MensajeEstado:="Componente rechazado";

            EsperarComponente;

            CapturarImagen;

            ClasificarComponente;

            ConfirmarClasificacionProc;

            RealizarPick;

            Realizaraproxpick;

            ConfirmarPickProc;

        ENDTEST

        ConfirmarPick:=0;

    ENDPROC

    PROC RealizarPlace()

        TEST Tipo

        CASE 1:

            MensajeEstado:="Almacenando resistencia";

            Path_12;

        CASE 2:

            MensajeEstado:="Almacenando capacitor";

            Path_13;

        CASE 3:

            MensajeEstado:="Almacenando conector";

            Path_14;

        CASE 4:

            MensajeEstado:="Almacenando CI";

            Path_15;

        ENDTEST

    ENDPROC

    PROC ConfirmarPlaceProc()

        MensajeEstado:="Esperando confirmación de PLACE";

        PlaceOK:=FALSE;

        WaitUntil ConfirmarPlace<>0;

        IF ConfirmarPlace=1 THEN

            MensajeEstado:="Componente almacenado";

            PlaceOK:=TRUE;

        ELSEIF ConfirmarPlace=2 THEN

            PlaceOK:=FALSE;

            MensajeEstado:="Place fallido";

            WaitTime 3;

        ENDIF

        ConfirmarPlace:=0;

        Path_10;

    ENDPROC

    PROC ActualizarInventario()

        MensajeEstado:="Almacén actualizado";

        TEST Tipo

        CASE 1:

            ContRes:=ContRes+1;

        CASE 2:

            ContCap:=ContCap+1;

        CASE 3:

            ContCon:=ContCon+1;

        CASE 4:

            ContCI:=ContCI+1;

        ENDTEST

        Total:=Total+1;

        Progreso:=Total;

    ENDPROC

    PROC FinEtapa()

        Estado:=4;

        FIN:=1;

        !Apagar todo

        Reset DO_01;
        Reset DO_05;
        Set DO_06;
        Reset FWD_Conveyor;
        Reset BWD_Conveyor;

        MensajeEstado:="¡Almacén listo!";

        WaitTime 3;

        MensajeEstado:="Esperando Nuevo almacén ...";

        WaitUntil BtnReset;

        BtnReset:=FALSE;

    ENDPROC

    PROC Path_10()
        MoveJ Target_Home,v100,z100,MyNewToolEI\WObj:=wobj0;
    ENDPROC

    PROC Path_11()
        MoveJ Target_35,v100,z10,MyNewToolEI\WObj:=Workobject_9;
        MoveL Target_36,v30,z10,MyNewToolEI\WObj:=Workobject_9;
    ENDPROC

    PROC Path_11_1()
        MoveL Target_30,v30,z10,MyNewToolEI\WObj:=Workobject_9;
        WaitTime 6;
        MoveL Target_36,v30,z10,MyNewToolEI\WObj:=Workobject_9;
    ENDPROC

    PROC Path_12()
        MoveL Target_35,v30,z10,MyNewToolEI\WObj:=Workobject_9;
        MoveJ Target_Home,v100,z10,MyNewToolEI\WObj:=wobj0;
        MoveJ Target_39,v100,z10,MyNewToolEI\WObj:=Workobject_13;
        MoveL Target_40,v30,z10,MyNewToolEI\WObj:=Workobject_13;
        Set DO_06;
        WaitTime 6;
        MoveJ Target_39,v30,z10,MyNewToolEI\WObj:=Workobject_13;
    ENDPROC

    PROC Path_13()
        MoveL Target_35,v30,z10,MyNewToolEI\WObj:=Workobject_9;
        MoveJ Target_Home,v100,z10,MyNewToolEI\WObj:=wobj0;
        MoveJ Target_49,v100,z10,MyNewToolEI\WObj:=Workobject_13;
        MoveL Target_50,v30,z10,MyNewToolEI\WObj:=Workobject_13;
        Set DO_06;
        WaitTime 6;
        MoveL Target_49,v30,z10,MyNewToolEI\WObj:=Workobject_13;
    ENDPROC

    PROC Path_14()
        MoveL Target_35,v30,z10,MyNewToolEI\WObj:=Workobject_9;
        MoveJ Target_Home,v100,z10,MyNewToolEI\WObj:=wobj0;
        MoveJ Target_59,v100,z10,MyNewToolEI\WObj:=Workobject_13;
        MoveL Target_60,v30,z10,MyNewToolEI\WObj:=Workobject_13;
        Set DO_06;
        WaitTime 6;
        MoveL Target_59,v30,z10,MyNewToolEI\WObj:=Workobject_13;
    ENDPROC

    PROC Path_15()
        MoveL Target_35,v30,z10,MyNewToolEI\WObj:=Workobject_9;
        MoveJ Target_Home,v100,z10,MyNewToolEI\WObj:=wobj0;
        MoveJ Target_69,v100,z10,MyNewToolEI\WObj:=Workobject_13;
        MoveL Target_70,v30,z10,MyNewToolEI\WObj:=Workobject_13;
        Set DO_06;
        WaitTime 6;
        MoveL Target_69,v30,z10,MyNewToolEI\WObj:=Workobject_13;
    ENDPROC


ENDMODULE