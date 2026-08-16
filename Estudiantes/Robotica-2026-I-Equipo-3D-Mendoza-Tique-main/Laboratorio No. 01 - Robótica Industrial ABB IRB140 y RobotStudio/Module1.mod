MODULE Module1

    CONST robtarget BaseDraw:=[[0,0,0],
    [0.694346616,0.10879539,-0.122149941,0.700803633],
    [-1,-1,0,0],
    [9E9,9E9,9E9,9E9,9E9,9E9]];

    CONST robtarget HOME:=[[-413.972133,684.456,139.157599],
    [0.989015864,0,-0.147809404,0],
    [0,0,0,0],
    [9E9,9E9,9E9,9E9,9E9,9E9]];

    CONST robtarget HOME2:=[[-370.116379342,684.456,-4.288115021],
    [0.989015864,0,-0.147809404,0],
    [0,0,0,0],
    [9E9,9E9,9E9,9E9,9E9,9E9]];

    CONST robtarget Target_aproximacion:=[[172.3445,164.9723,-139.7743],
    [0.694346616,0.10879539,-0.122149941,0.700803633],
    [-1,-1,0,0],
    [9E9,9E9,9E9,9E9,9E9,9E9]];

    VAR robtarget pActual;

    CONST num l_width := 40;
    CONST num l_height := 60;
    CONST num l_space := 15;

    CONST num z_draw := 0;  !No escribe bien? bajarle a 5 mm positivos
    CONST num z_lift := -20;

    PROC main()

        
        
        !Configuración Banda Real
        Set BWD_Conveyor;
        WaitTime 2;
        Reset BWD_Conveyor;
        
        
        WHILE TRUE DO
            IF DI_01 = 1 THEN
                
                !Prende testigo luz
                Set DO_01;
                !Aarranca Banda
                Set FWD_Conveyor;
                WaitTime 2;
                Reset FWD_Conveyor;
                
                
                !Aproximación y Dibujo
                MoveJ HOME, v1000, z100, MyNewTool \WObj:=Workobject_1;
                MoveJ HOME2, v800, z50, MyNewTool \WObj:=Workobject_1;
        
                MoveJ Target_aproximacion, v500, z50, MyNewTool \WObj:=Workobject_1;
                MoveL Offs(Target_aproximacion, 0, 0, 20), v300, z10, MyNewTool \WObj:=Workobject_1;
        
                ! ===== LUIS =====
                pActual := Offs(BaseDraw, 30, 20, 0);
        
                Draw_L;  pActual := Offs(pActual, l_width + l_space, 0, 0);
                Draw_U;  pActual := Offs(pActual, l_width + l_space, 0, 0);
                Draw_I;  pActual := Offs(pActual, l_width + l_space, 0, 0);
                Draw_S;
        
                ! ===== DUVAN =====
                pActual := Offs(BaseDraw, 10, 110, 0);
        
                Draw_D;  pActual := Offs(pActual, l_width + l_space, 0, 0);
                Draw_U;  pActual := Offs(pActual, l_width + l_space, 0, 0);
                Draw_V;  pActual := Offs(pActual, l_width + l_space, 0, 0);
                Draw_A;  pActual := Offs(pActual, l_width + l_space, 0, 0);
                Draw_N;
        
                MoveL Offs(Target_aproximacion, 0, 0, 20), v300, z10, MyNewTool \WObj:=Workobject_1;
        
                MoveJ Target_aproximacion, v500, z50, MyNewTool \WObj:=Workobject_1;
                MoveJ HOME2, v800, z50, MyNewTool \WObj:=Workobject_1;
                MoveJ HOME, v1000, fine, MyNewTool \WObj:=Workobject_1;

                
                
                !Se va el pastel
                Set FWD_Conveyor;
                WaitTime 2;
                Reset FWD_Conveyor;
                
                
                !Apaga testigo luz
                Reset DO_01;
        
            ENDIF
        ENDWHILE
                
                
    ENDPROC

    PROC Lift()
        MoveL Offs(pActual, 0, 0, z_lift), v200, z1, MyNewTool \WObj:=Workobject_1;
    ENDPROC

    PROC Touch()
        MoveL Offs(pActual, 0, 0, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
    ENDPROC

    PROC Draw_L()
        Lift; Touch;
        MoveL Offs(pActual, 0, l_height, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        MoveL Offs(pActual, l_width, l_height, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        MoveL Offs(pActual, l_width, l_height-10, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        MoveL Offs(pActual, 10, l_height-10, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        MoveL Offs(pActual, 10, 0, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        MoveL Offs(pActual, 0, 0, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        Lift;
    ENDPROC

    PROC Draw_U()
        Lift; Touch;
        MoveL Offs(pActual, 0, l_height, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        MoveL Offs(pActual, 0, 0, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        MoveL Offs(pActual, l_width, 0, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        MoveL Offs(pActual, l_width, l_height, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        MoveL Offs(pActual, l_width-10, l_height, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        MoveL Offs(pActual, l_width-10, 10, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        MoveL Offs(pActual, 10, 10, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        MoveL Offs(pActual, 10, l_height, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        MoveL Offs(pActual, 0, l_height, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        Lift;
    ENDPROC

    PROC Draw_I()
        Lift; Touch;
        MoveL Offs(pActual, l_width/2-5, 0, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        MoveL Offs(pActual, l_width/2+5, 0, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        MoveL Offs(pActual, l_width/2+5, l_height, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        MoveL Offs(pActual, l_width/2-5, l_height, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        MoveL Offs(pActual, l_width/2-5, 0, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        Lift;
    ENDPROC

    PROC Draw_S()
        Lift; Touch;
        MoveL Offs(pActual, l_width, l_height, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        MoveL Offs(pActual, 0, l_height, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        MoveL Offs(pActual, 0, l_height/2, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        MoveL Offs(pActual, l_width, l_height/2, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        MoveL Offs(pActual, l_width, 0, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        MoveL Offs(pActual, 0, 0, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        MoveL Offs(pActual, 0, 10, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        MoveL Offs(pActual, l_width-10, 10, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        MoveL Offs(pActual, l_width-10, l_height/2-10, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        MoveL Offs(pActual, 10, l_height/2-10, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        MoveL Offs(pActual, 10, l_height-10, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        MoveL Offs(pActual, l_width, l_height-10, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        Lift;
    ENDPROC

    PROC Draw_D()
        Lift; Touch;
        MoveL Offs(pActual, 0, 0, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        MoveL Offs(pActual, 0, l_height, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        MoveL Offs(pActual, l_width, l_height-10, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        MoveL Offs(pActual, l_width, 10, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        MoveL Offs(pActual, 0, 0, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        Lift;
    ENDPROC

    PROC Draw_V()
        Lift; Touch;
        MoveL Offs(pActual, 0, l_height, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        MoveL Offs(pActual, l_width/2, 0, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        MoveL Offs(pActual, l_width, l_height, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        MoveL Offs(pActual, l_width-10, l_height, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        MoveL Offs(pActual, l_width/2, 10, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        MoveL Offs(pActual, 10, l_height, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        MoveL Offs(pActual, 0, l_height, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        Lift;
    ENDPROC

    PROC Draw_A()
        Lift; Touch;
        MoveL Offs(pActual, 0, 0, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        MoveL Offs(pActual, l_width/2, l_height, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        MoveL Offs(pActual, l_width, 0, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        MoveL Offs(pActual, l_width-10, 0, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        MoveL Offs(pActual, l_width*0.7, l_height/2, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        MoveL Offs(pActual, l_width*0.3, l_height/2, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        MoveL Offs(pActual, 10, 0, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        MoveL Offs(pActual, 0, 0, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        Lift;
    ENDPROC

    PROC Draw_N()
        Lift; Touch;
        MoveL Offs(pActual, 0, 0, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        MoveL Offs(pActual, 0, l_height, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        MoveL Offs(pActual, l_width, 0, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        MoveL Offs(pActual, l_width, l_height, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        MoveL Offs(pActual, l_width-10, l_height, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        MoveL Offs(pActual, l_width-10, 10, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        MoveL Offs(pActual, 10, l_height, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        MoveL Offs(pActual, 0, l_height, z_draw), v100, fine, MyNewTool \WObj:=Workobject_1;
        Lift;
    ENDPROC

ENDMODULE