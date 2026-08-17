MODULE Module1
    VAR speeddata v_General := v100;
    

    CONST robtarget Target_p6:=[[137.5,26,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_p7:=[[110,10,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_Home:=[[1276.201091317,270.865751635,-223.344323264],[0.000128418,-0.283476378,0.00041989,-0.958979119],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_wo00:=[[0,0,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_Mid:=[[650.50732426,-179.71223486,-321.671455648],[0.659869676,0.287533933,-0.254057883,0.646026965],[0,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_Mid_2:=[[280.993316271,-234.731899404,-302.770809799],[0.69921632,0.140892404,-0.105213759,0.69294728],[1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_p1:=[[137.5,26,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_p1top2:=[[128,11,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_p2:=[[110,10,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_p2top3:=[[60,36,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_p3:=[[15,72.25,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_p3top4:=[[12.5,75.5,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_p4:=[[15,79.25,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_p4top5:=[[68,111,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_p5:=[[128.5,115,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_p5top6:=[[134,111,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_p7top8:=[[107.5,15,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_p8:=[[110,20,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_p8top9:=[[90,50,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_p9:=[[61,74,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_p9top3:=[[40,78,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_p5top10:=[[124,76,0],[1,0,0,0],[0,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_p10:=[[128.5,36,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_p10top1:=[[134,32.5,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_pD1:=[[200,180,0],[1,0,0,0],[0,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_pD3:=[[180,200,0],[1,0,0,0],[0,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_pD2:=[[160,180,0],[1,0,0,0],[0,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_pA1:=[[160,200,0],[1,0,0,0],[0,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_pA2:=[[200,215,0],[1,0,0,0],[0,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_pA3:=[[160,230,0],[1,0,0,0],[0,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_pA4:=[[180,205,0],[1,0,0,0],[0,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_pV1:=[[200,230,0],[1,0,0,0],[0,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_pV2:=[[160,245,0],[1,0,0,0],[0,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_pV3:=[[200,260,0],[1,0,0,0],[0,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_pI1:=[[200,270,0],[1,0,0,0],[0,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_pI2:=[[160,270,0],[1,0,0,0],[0,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_pDD2:=[[160,280,0],[1,0,0,0],[0,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_pDD3:=[[180,300,0],[1,0,0,0],[0,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_pDD1:=[[200,280,0],[1,0,0,0],[0,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_pL1:=[[120,180,0],[1,0,0,0],[0,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_pL2:=[[80,180,0],[1,0,0,0],[0,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_pL3:=[[80,200,0],[1,0,0,0],[0,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_pU1:=[[120,210,0],[1,0,0,0],[0,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_pU2:=[[90,210,0],[1,0,0,0],[0,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_pU3:=[[80,220,0],[1,0,0,0],[0,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_pU4:=[[90,230,0],[1,0,0,0],[0,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_pU5:=[[120,230,0],[1,0,0,0],[0,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_pII1:=[[120,240,0],[1,0,0,0],[0,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_pII2:=[[80,240,0],[1,0,0,0],[0,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_pS1:=[[120,260,0],[1,0,0,0],[0,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_pS2:=[[110,250,0],[1,0,0,0],[0,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_pS3:=[[100,260,0],[1,0,0,0],[0,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_pS4:=[[90,270,0],[1,0,0,0],[0,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_pS5:=[[80,260,0],[1,0,0,0],[0,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_Rest:=[[1237.348278983,71.895073343,-151.281356209],[0.000128418,-0.283476378,0.00041989,-0.958979119],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    PERS tooldata Trazador:=[TRUE,[[27.808,-0.475,170.341],[0.965925826,0,0.258819045,0]],[1,[0,0,1],[1,0,0,0],0,0,0]];
    TASK PERS wobjdata Workobject_Tarta:=[FALSE,TRUE,"",[[0,0,0],[1,0,0,0]],[[-660,320,405],[0.00043882,0.999672,0.000015367,-0.0256151]]];

    ! --- 4. RUTINA PRINCIPAL ---
    PROC main()
        ! Bucle infinito para revisar las entradas constantemente
        WHILE TRUE DO
            IF DI_01 = 1 THEN
            
                Set FWD_Conveyor;
                waitTime 3;
                Reset FWD_Conveyor; 
                SetDO DO_01,1;
                
                MoveJ Target_Home,v_General,z10,Trazador\WObj:=Workobject_Tarta;
                EjecutarTrazos;
                MoveJ Target_Mid_2,v_General,z10,Trazador\WObj:=Workobject_Tarta;
                MoveJ Target_Mid,v_General,z10,Trazador\WObj:=Workobject_Tarta;
                MoveJ Target_Home,v_General,z10,Trazador\WObj:=Workobject_Tarta;
                
                Set FWD_Conveyor;
                waitTime 3;
                Reset FWD_Conveyor; 
                SetDO DO_01, 0;
            ENDIF
            
            IF DI_02 = 1 THEN
                SetDO DO_02,1;
                Path_HometoRest;
                SetDO DO_02,0;
            ENDIF
                
            IF DI_03 = 1 THEN
                Set FWD_Conveyor;
                Set BWD_Conveyor;
                waitTime 3;
                Reset BWD_Conveyor;
                Reset FWD_Conveyor; 
                
            ENDIF
            
            
            
            WaitTime 0.1; ! Pequeña pausa para no sobrecargar la CPU del controlador
        ENDWHILE
    ENDPROC

    ! --- NUEVO: Procedimiento para levantar, moverse y posicionarse arriba de la siguiente letra ---
    PROC MoverEntreLetras(robtarget pInicio, robtarget pDestino)
        ! 1. Sube 50 mm en Z desde el punto donde terminó el trazo actual
        MoveL Offs(pInicio, 0, 0, -50), v_General, z10, Trazador\WObj:=Workobject_Tarta;
        ! 2. Se desplaza en el aire y se posiciona 50 mm por encima del inicio del próximo trazo
        MoveL Offs(pDestino, 0, 0, -50), v_General, z10, Trazador\WObj:=Workobject_Tarta;
    ENDPROC

    ! --- 5. RUTINA DE TRAZOS MODIFICADA (Trazos continuos + Saltos) ---
    PROC EjecutarTrazos()
        ! --- Trazos iniciales conectados (Termina en p1) ---
        !Path_Hometowo;
        !Path_wotoHome;
        Path_Hometop1;
        Path_p1top2;
        Path_p2top3;
        Path_p3top4;
        Path_p4top5;
        Path_p5top6;
        Path_p6p7;
        Path_p7top8;
        Path_p9top3; 
        Path_p5top10;
        Path_p10top1; ! (Termina en Target_p1)
        
        ! --- SALTO Y LETRA D ---
        MoverEntreLetras Target_p1, Target_pD1;
        Path_pD1D3D2;
        Path_D2D1; ! (Termina en Target_pD1)
        
        ! --- SALTO Y LETRA A ---
        MoverEntreLetras Target_pD1, Target_pA1;
        Path_A1A2;
        Path_A2A3;
        Path_A3A4; ! (Termina en Target_pA4)
        
        ! --- SALTO Y LETRA V ---
        MoverEntreLetras Target_pA4, Target_pV1;
        Path_V1V2;
        Path_V2V3; ! (Termina en Target_pV3)
        
        ! --- SALTO Y LETRA I ---
        MoverEntreLetras Target_pV3, Target_pI1;
        Path_I1I2; ! (Termina en Target_pI2)
        
        ! --- SALTO Y LETRA D ---
        MoverEntreLetras Target_pI2, Target_pDD2;
        Path_DD1DD3DD2;
        Path_DD2DD1; ! (Termina en Target_pDD2)
        
        ! --- SALTO Y LETRA L ---
        MoverEntreLetras Target_pDD2, Target_pL1;
        Path_L1L2;
        Path_L2L3; ! (Termina en Target_pL3)
        
        ! --- SALTO Y LETRA U ---
        MoverEntreLetras Target_pL3, Target_pU1;
        Path_U1U2;
        Path_U2U3U4;
        Path_U4U5; ! (Termina en Target_pU5)
        
        ! --- SALTO Y LETRA I ---
        MoverEntreLetras Target_pU5, Target_pII1;
        Path_II1II2; ! (Termina en Target_pII2)
        
        ! --- SALTO Y LETRA S ---
        MoverEntreLetras Target_pII2, Target_pS1;
        Path_S1S2S3;
        Path_S3S4S5; ! (Termina en Target_pS5)
        
        ! --- SALTO FINAL Y REGRESO ---
        MoverEntreLetras Target_pS5, Target_wo00;
        Path_wotoHome;
    ENDPROC

    ! --- 6. PROCEDIMIENTOS DE MOVIMIENTO ---
    PROC Path_p6p7()
        MoveL Target_p6,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        MoveL Target_p7,v_General,z10,Trazador\WObj:=Workobject_Tarta;
    ENDPROC

    PROC Path_Hometowo()
        MoveJ Target_Home,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        MoveJ Target_Mid,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        MoveJ Target_Mid_2,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        MoveJ Target_wo00,v_General,z10,Trazador\WObj:=Workobject_Tarta;
       
    ENDPROC

    PROC Path_wotoHome()
        MoveJ Target_wo00,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        MoveJ Target_Mid_2,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        MoveJ Target_Mid,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        MoveJ Target_Home,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        
    ENDPROC

    PROC Path_Hometop1()
        MoveJ Target_Home,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        MoveJ Target_Mid,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        MoveJ Target_Mid_2,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        MoveJ Target_p1,v_General,z10,Trazador\WObj:=Workobject_Tarta;
    ENDPROC

    PROC Path_p1top2()
        MoveL Target_p1,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        MoveC Target_p1top2,Target_p2,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        !MoveL Target_p1top2,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        !MoveL Target_p2,v_General,z10,Trazador\WObj:=Workobject_Tarta;
    ENDPROC

    PROC Path_p2top3()
        MoveL Target_p2,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        MoveC Target_p2top3,Target_p3,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        !MoveL Target_p2top3,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        !MoveL Target_p3,v_General,z10,Trazador\WObj:=Workobject_Tarta;
    ENDPROC

    PROC Path_p3top4()
        MoveL Target_p3,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        MoveC Target_p3top4,Target_p4,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        !MoveL Target_p3top4,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        !MoveL Target_p4,v_General,z10,Trazador\WObj:=Workobject_Tarta;
    ENDPROC

    PROC Path_p4top5()
        MoveL Target_p4,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        MoveL Target_p4top5,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        MoveL Target_p5,v_General,z10,Trazador\WObj:=Workobject_Tarta;
    ENDPROC

    PROC Path_p5top6()
        MoveL Target_p5,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        MoveL Target_p5top6,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        MoveL Target_p6,v_General,z10,Trazador\WObj:=Workobject_Tarta;
    ENDPROC

    PROC Path_p7top8()
        MoveL Target_p7,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        MoveL Target_p7top8,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        MoveL Target_p8,v_General,z10,Trazador\WObj:=Workobject_Tarta;
    ENDPROC

    PROC Path_p8top9()
        MoveL Target_p8,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        MoveC Target_p8top9,Target_p9,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        !MoveL Target_p8top9,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        !MoveL Target_p9,v_General,z10,Trazador\WObj:=Workobject_Tarta;
    ENDPROC

    PROC Path_p9top3()
        MoveL Target_p9,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        MoveC Target_p9top3,Target_p3,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        !MoveL Target_p9top3,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        !MoveL Target_p3,v_General,z10,Trazador\WObj:=Workobject_Tarta;
    ENDPROC

    PROC Path_p5top10()
        MoveL Target_p5,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        MoveC Target_p5top10,Target_p10,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        !MoveL Target_p5top10,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        !MoveL Target_p10,v_General,z10,Trazador\WObj:=Workobject_Tarta;
    ENDPROC

    PROC Path_p10top1()
        MoveL Target_p10,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        MoveL Target_p10top1,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        MoveL Target_p1,v_General,z10,Trazador\WObj:=Workobject_Tarta;
    ENDPROC

    PROC Path_pD1D3D2()
        MoveL Target_pD1,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        MoveC Target_pD3,Target_pD2,v_General,z10,Trazador\WObj:=Workobject_Tarta;

    ENDPROC

    PROC Path_D2D1()
        MoveL Target_pD2,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        MoveL Target_pD1,v_General,z10,Trazador\WObj:=Workobject_Tarta;
    ENDPROC

    PROC Path_A1A2()
        MoveL Target_pA1,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        MoveL Target_pA2,v_General,z10,Trazador\WObj:=Workobject_Tarta;
    ENDPROC

    PROC Path_A2A3()
        MoveL Target_pA2,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        MoveL Target_pA3,v_General,z10,Trazador\WObj:=Workobject_Tarta;
    ENDPROC

    PROC Path_A3A4()
        MoveL Target_pA3,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        MoveL Target_pA4,v_General,z10,Trazador\WObj:=Workobject_Tarta;
    ENDPROC

    PROC Path_V1V2()
        MoveL Target_pV1,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        MoveL Target_pV2,v_General,z10,Trazador\WObj:=Workobject_Tarta;
    ENDPROC

    PROC Path_V2V3()
        MoveL Target_pV2,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        MoveL Target_pV3,v_General,z10,Trazador\WObj:=Workobject_Tarta;
    ENDPROC

    PROC Path_I1I2()
        MoveL Target_pI1,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        MoveL Target_pI2,v_General,z10,Trazador\WObj:=Workobject_Tarta;
    ENDPROC

    PROC Path_DD1DD3DD2()
        MoveL Target_pDD2,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        MoveC Target_pDD3,Target_pDD1,v_General,z10,Trazador\WObj:=Workobject_Tarta;

    ENDPROC

    PROC Path_DD2DD1()
        MoveL Target_pDD1,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        MoveL Target_pDD2,v_General,z10,Trazador\WObj:=Workobject_Tarta;
    ENDPROC

    PROC Path_L1L2()
        MoveL Target_pL1,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        MoveL Target_pL2,v_General,z10,Trazador\WObj:=Workobject_Tarta;
    ENDPROC

    PROC Path_L2L3()
        MoveL Target_pL2,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        MoveL Target_pL3,v_General,z10,Trazador\WObj:=Workobject_Tarta;
    ENDPROC

    PROC Path_U1U2()
        MoveL Target_pU1,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        MoveL Target_pU2,v_General,z10,Trazador\WObj:=Workobject_Tarta;
    ENDPROC

    PROC Path_U2U3U4()
        MoveL Target_pU2,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        MoveC Target_pU3,Target_pU4,v_General,z10,Trazador\WObj:=Workobject_Tarta;

    ENDPROC

    PROC Path_U4U5()
        MoveL Target_pU4,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        MoveL Target_pU5,v_General,z10,Trazador\WObj:=Workobject_Tarta;
    ENDPROC

    PROC Path_II1II2()
        MoveL Target_pII1,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        MoveL Target_pII2,v_General,z10,Trazador\WObj:=Workobject_Tarta;
    ENDPROC

    PROC Path_S1S2S3()
        MoveL Target_pS1,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        MoveC Target_pS2,Target_pS3,v_General,z10,Trazador\WObj:=Workobject_Tarta;
    ENDPROC

    PROC Path_S3S4S5()
        MoveL Target_pS3,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        MoveC Target_pS4,Target_pS5,v_General,z10,Trazador\WObj:=Workobject_Tarta;
    ENDPROC

    PROC Path_HometoRest()
        MoveJ Target_Rest,v_General,z10,Trazador\WObj:=Workobject_Tarta;
    ENDPROC
    PROC Path_pDD1DD3DD2()
        MoveL Target_pDD1,v_General,z10,Trazador\WObj:=Workobject_Tarta;
        MoveC Target_pDD3,Target_pDD2,v_General,z10,Trazador\WObj:=Workobject_Tarta;
    ENDPROC

ENDMODULE