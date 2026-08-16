```python
MODULE Module1  
    PERS tooldata Marcador:=[TRUE,[[85.45,-1.13,118.934],[0.866025404,0,0.5,0]],[1,[0,0,1],[1,0,0,0],0,0,0]];
    TASK PERS wobjdata Pastel:=[FALSE,TRUE,"",[[0,0,0],[1,0,0,0]],[[193.076,-670.653,608.055],[0.0163836,0.000445408,0.999496,-0.0271948]]];
    !TASK PERS wobjdata Pastel:=[FALSE,TRUE,"",[[0,0,0],[1,0,0,0]],[[387.5,-582.5,530],[0,0,1,0]]];
    !PERS tooldata Marcador_real:=[TRUE,[[100.689,-0.535,124.792],[0.866025404,0,0.5,0]],[1,[0,0,1],[1,0,0,0],0,0,0]];!Real
    !TASK PERS wobjdata caja1:=[FALSE,TRUE,"",[[0,0,0],[1,0,0,0]],[[218.446,-619.836,751.747],[0.0244979,-0.017695,0.99947,-0.0120801]]]; 
     
    CONST robtarget C1_1:=[[62.708,129.951,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget C1_1_prev:=[[62.708,129.951,-35],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget C1_2:=[[55.084,138.485,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget C1_3:=[[25.976,105.902,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget C1_3_1:=[[22.184,86.907,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget C1_3_2:=[[28.1,78.429,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget C1_3_3:=[[46.089,75.022,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget C1_4:=[[55.461,81.699,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget C1_4_1:=[[65.303,74.876,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget C1_4_2:=[[78.268,75.655,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget C1_4_3:=[[86.718,82.787,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget C1_5:=[[89.527,96.39,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget C1_5_1:=[[94.654,105.724,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget C2_1:=[[91.318,115.837,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget C2_2:=[[70.709,138.907,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget C2_3:=[[50.099,115.837,-1.5],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget C2_3_1:=[[47.524,102.349,-1.5],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget C2_3_2:=[[51.584,96.633,-1.5],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget C2_3_3:=[[60.935,93.633,-1.5],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget C2_4:=[[70.709,98.919,-1.5],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget C2_4_1:=[[79.59,93.722,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_Home:=[[566.56651662,-1.13,546.031129247],[0,0,1,0],[0,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget C1_5_post:=[[89.527,96.39,-55],[1,0,0,0],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget R_1:=[[174.846,48.633,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget R_1prev:=[[174.846,48.633,-20],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget R_2:=[[174.152,29.455,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget R_3:=[[174.069,33.896,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget R_3_1:=[[178.343,29.428,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget R_4:=[[180.619,28.817,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget R_4_post:=[[180.619,28.817,-21],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget R_1_prev:=[[174.846,48.633,-21],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_2_1:=[[92.613,35.228,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_2_1_1:=[[191.04,31.37,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_2_1_prev:=[[92.613,35.228,-30],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_2_2:=[[103.131,37.115,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_2_2_1:=[[198.291,34.638,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_2_3:=[[103.131,44.455,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_2_4:=[[103.112,38.788,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_2_4_1:=[[195.717,47.245,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_2_5:=[[103.345,50.393,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_2_5_1:=[[190.041,47.19,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_2_6:=[[189.084,44.553,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_2_6_1:=[[192.872,39.948,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_2_7:=[[198.631,38.42,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_2_8:=[[198.631,50.409,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_2_8_post:=[[198.631,50.409,-21],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget S_1:=[[138.294,62.758,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget S_1_prev:=[[138.294,62.758,-21],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget S_2:=[[138.294,85.239,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget S_2_post:=[[138.294,85.239,-21],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget S_3:=[[127.053,73.999,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget S_3_prev:=[[127.053,73.999,-21],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget S_4:=[[149.534,73.999,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget S_4_post:=[[149.534,73.999,-21],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget J_1:=[[152.914,131.323,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget J_1_1:=[[159.76,128.444,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget J_1_prev:=[[152.914,131.323,-21],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget J_2:=[[162.628,123.497,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget J_3:=[[163.429,93.422,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget J_4:=[[163.429,93.422,-21],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget J_3_post:=[[163.429,93.422,-21],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget U_1:=[[173.05,104.784,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget U_1_prev:=[[173.05,104.784,-21],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget U_2:=[[173.261,118.619,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget U_2_1:=[[176.474,122.566,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget U_3:=[[181.954,122.804,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget U_3_1:=[[186.357,120.028,-0.843],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget U_4:=[[187.475,115.982,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget U_5:=[[187.412,104.458,-1],[1,0,0,0],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget U_5_post:=[[187.412,104.458,-21],[1,0,0,0],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_3_1_prev:=[[188.112,35.228,-21],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_3_1:=[[188.112,35.228,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_3_1_1:=[[191.04,31.37,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_3_2:=[[195.537,31.558,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_3_2_1:=[[198.291,34.638,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_3_3:=[[198.631,37.115,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_3_4:=[[198.631,44.47,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_3_4_1:=[[195.717,47.245,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_3_5:=[[192.525,48.189,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_3_5_1:=[[190.041,47.19,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_3_6:=[[189.084,44.553,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_3_6_1:=[[192.872,39.948,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_3_7:=[[198.631,38.42,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_3_8:=[[198.631,50.409,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_3_8_post:=[[198.631,50.409,-21],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_4_1:=[[200.692,107.416,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_4_1_1:=[[202.026,104.276,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_4_1_prev:=[[200.692,107.416,-21],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_4_2:=[[206.665,103.414,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_4_2_1:=[[209.986,105.143,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_4_3:=[[211.196,109.342,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_4_4:=[[211.187,116.709,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_4_4_1:=[[208.168,119.542,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_4_5:=[[204.11,120.299,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_4_5_1:=[[201.84,118.116,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_4_6:=[[202.616,113.8,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_4_6_1:=[[206.118,111.946,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_4_7:=[[211.185,110.871,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_4_8:=[[211.314,122.627,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_4_8_post:=[[211.196,122.636,-21],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget N_2_1:=[[227.466,120.51,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget N_2_1_prev:=[[227.466,120.51,-21],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget N_2_2:=[[227.206,101.172,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget N_2_3:=[[227.472,107.409,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget N_2_3_1:=[[230.614,104.265,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget N_2_4:=[[236.261,104.768,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget N_2_4_1:=[[238.307,112.359,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget N_2_5:=[[237.908,122.499,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget N_2_5_post:=[[237.908,122.499,-21],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_1_1:=[[14.209,47.662,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_1_1_prev:=[[14.209,47.662,-30],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_1_2:=[[23.673,24.432,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_1_3:=[[33.248,47.995,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_1_3_pos:=[[33.248,47.995,-30],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_1_4:=[[18.039,37.837,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_1_4_prev:=[[18.039,37.837,-30],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_1_5:=[[29.279,37.837,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_1_5_post:=[[29.279,37.837,-30],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget L_1:=[[51.177,17.244,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget L_1_prev:=[[51.177,17.244,-30],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget L_2:=[[51.066,48.3,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget L_2_post:=[[51.066,48.3,-30],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget E_1:=[[61.196,37.893,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget E_1_prev:=[[61.196,37.893,-30],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget E_2:=[[72.047,37.893,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget E_2_1:=[[71.27,32.925,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget E_3:=[[66.719,30.399,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget E_4:=[[61.14,39.585,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget E_4_1:=[[63.388,46.274,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget E_4_2:=[[69.016,48.55,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget E_5:=[[75.156,46.496,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget E_5_post:=[[75.156,46.496,-30],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget JA_1_prev:=[[77.376,30.538,-30],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget JA_2:=[[84.897,28.678,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget JA_3:=[[84.814,48.383,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget JA_3_1:=[[83.504,57.924,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget JA_4:=[[76.044,63.12,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget JA_4_post:=[[76.044,63.12,-30],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget JA_1:=[[77.376,30.538,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_2_1_2:=[[95.256,31.454,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_2_1_3:=[[100.625,31.841,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_2_3_1:=[[98.326,48.04,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_2_3_2:=[[94.343,46.962,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_2_3_3:=[[94.417,41.739,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_2_3_4:=[[98.277,39.648,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_2_5_post:=[[103.345,50.393,-30],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget A_2_2_2:=[[102.728,34.436,0],[1,0,0,0],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget N_1_0:=[[119.173,29.206,-30],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget N_1_1:=[[119.173,30.066,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget N_1_2:=[[119.589,48.578,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget N_1_3:=[[119.423,35.117,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget N_1_3_2:=[[122.874,31.924,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget N_1_3_3:=[[126.663,31.829,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget N_1_3_4:=[[129.441,33.849,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget N_1_4:=[[130.229,37.62,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget N_1_5:=[[129.83,50.409,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget N_1_5_post:=[[129.83,50.409,-30],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget D_1:=[[156.723,34.007,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget D_1_2:=[[150.035,30.704,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget D_1_3:=[[144.521,34.085,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget D_1_4:=[[143.54,39.086,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget D_1_5:=[[144.839,44.625,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget D_1_6:=[[150.562,48.05,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget D_1_7:=[[154.918,46.147,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget D_2:=[[156.723,39.474,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget D_3:=[[156.723,22.073,-1],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget D_4:=[[156.474,50.409,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget D_4_post:=[[156.474,50.409,-30],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget D_0:=[[156.723,34.007,-30],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_Mantenimiento:=[[44.047400828,895.336736731,623.833566648],[0.259155503,-0.657904572,0.702561397,0.08004676],[0,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    PROC main()
        WHILE TRUE DO 
            IF DI_03 = 1 THEN
                SET DO_03;
                SET BWD_Conveyor;
                waittime 4;
                RESET BWD_Conveyor;
                RESET DO_03;
            ENDIF
                
            IF DI_01 = 1 THEN
                SET FWD_Conveyor;
                waittime 4;
                Reset FWD_Conveyor; 
                WaitTime 5;
                SET DO_01; 
                Path_Home; 
                Path_A_1; 
                Path_L;
                Path_E;
                Path_JA;
                Path_A_2;
                Path_N_1;
                Path_D; 
                Path_R; 
                Path_A_3; 
                Path_S; 
                Path_J; 
                Path_U; 
                Path_A_4; 
                Path_N_2;
                Path_10;
                Path_Home; 
                SET FWD_Conveyor;
                waittime 4;
                Reset FWD_Conveyor; 
                RESET DO_01;
            ENDIF
            IF DI_02 = 1 THEN
                SET DO_02;
                Path_Mantenimiento;
                WaitTime 1; 
                Path_Home;
                RESET DO_02;
            ENDIF
        ENDWHILE
  ENDPROC
    PROC Path_10()
        MoveJ C1_1_prev,v100,z10,Marcador\WObj:=Pastel;
        MoveL C1_1,v100,z10,Marcador\WObj:=Pastel;
        MoveL C1_2,v100,z10,Marcador\WObj:=Pastel;
        MoveL C1_3,v100,z10,Marcador\WObj:=Pastel;
        MoveC C1_3_1,C1_3_2,v100,z10,Marcador\WObj:=Pastel;
        MoveC C1_3_3,C1_4,v100,z10,Marcador\WObj:=Pastel;
        MoveC C1_4_1,C1_4_2,v100,z10,Marcador\WObj:=Pastel;
        MoveC C1_4_3,C1_5,v100,z1,Marcador\WObj:=Pastel;
        MoveC C1_5_1,C2_1,v100,z10,Marcador\WObj:=Pastel;
        MoveL C2_2,v100,z10,Marcador\WObj:=Pastel;
        MoveL C2_3,v100,z10,Marcador\WObj:=Pastel;
        MoveC C2_3_1,C2_3_2,v100,z10,Marcador\WObj:=Pastel;
        MoveC C2_3_3,C2_4,v100,z10,Marcador\WObj:=Pastel;
        MoveC C2_4_1,C1_5,v100,z10,Marcador\WObj:=Pastel;
        MoveL C1_5_post,v100,z1,Marcador\WObj:=Pastel;
    ENDPROC
    PROC Path_Home()
        MoveJ Target_Home,v100,z100,Marcador\WObj:=wobj0;
    ENDPROC
    PROC Path_R()
        MoveJ R_1_prev,v100,z10,Marcador\WObj:=Pastel;
        MoveL R_1,v100,z10,Marcador\WObj:=Pastel;
        MoveL R_2,v100,z10,Marcador\WObj:=Pastel;
        MoveL R_3,v100,z10,Marcador\WObj:=Pastel;
        MoveC R_3_1,R_4,v100,z10,Marcador\WObj:=Pastel;
        MoveL R_4_post,v100,z10,Marcador\WObj:=Pastel;
    ENDPROC
    PROC Path_S()
        MoveJ S_1_prev,v100,z10,Marcador\WObj:=Pastel;
        MoveL S_1,v100,z10,Marcador\WObj:=Pastel;
        MoveL S_2,v100,z10,Marcador\WObj:=Pastel;
        MoveL S_2_post,v100,z10,Marcador\WObj:=Pastel;
        MoveL S_3_prev,v100,z10,Marcador\WObj:=Pastel;
        MoveL S_3,v100,z10,Marcador\WObj:=Pastel;
        MoveL S_4,v100,z10,Marcador\WObj:=Pastel;
        MoveL S_4_post,v100,z10,Marcador\WObj:=Pastel;
    ENDPROC
    PROC Path_J()
        MoveJ J_1_prev,v100,z10,Marcador\WObj:=Pastel;
        MoveL J_1,v100,z10,Marcador\WObj:=Pastel;
        MoveC J_1_1,J_2,v100,z10,Marcador\WObj:=Pastel;
        MoveL J_3,v100,z10,Marcador\WObj:=Pastel;
        MoveL J_3_post,v100,z10,Marcador\WObj:=Pastel;
    ENDPROC
    PROC Path_U()
        MoveJ U_1_prev,v100,z10,Marcador\WObj:=Pastel;
        MoveL U_1,v100,z10,Marcador\WObj:=Pastel;
        MoveL U_2,v100,z10,Marcador\WObj:=Pastel;
        MoveC U_2_1,U_3,v100,z10,Marcador\WObj:=Pastel;
        MoveL U_3_1,v100,z10,Marcador\WObj:=Pastel;
        MoveL U_4,v100,z10,Marcador\WObj:=Pastel;
        MoveL U_5,v100,z10,Marcador\WObj:=Pastel;
        MoveL U_5_post,v100,z10,Marcador\WObj:=Pastel;
    ENDPROC
    PROC Path_A_3()
        MoveJ A_3_1_prev,v100,z10,Marcador\WObj:=Pastel;
        MoveL A_3_1,v100,z10,Marcador\WObj:=Pastel;
        MoveC A_3_1_1,A_3_2,v100,z10,Marcador\WObj:=Pastel;
        MoveC A_3_2_1,A_3_3,v100,z10,Marcador\WObj:=Pastel;
        MoveL A_3_4,v100,z10,Marcador\WObj:=Pastel;
        MoveC A_3_4_1,A_3_5,v100,z10,Marcador\WObj:=Pastel;
        MoveC A_3_5_1,A_3_6,v100,z10,Marcador\WObj:=Pastel;
        MoveC A_3_6_1,A_3_7,v100,z10,Marcador\WObj:=Pastel;
        MoveL A_3_8,v100,z10,Marcador\WObj:=Pastel;
        MoveL A_3_8_post,v100,z10,Marcador\WObj:=Pastel;
    ENDPROC
    PROC Path_A_4()
        MoveJ A_4_1_prev,v100,z10,Marcador\WObj:=Pastel;
        MoveL A_4_1,v100,z10,Marcador\WObj:=Pastel;
        MoveC A_4_1_1,A_4_2,v100,z10,Marcador\WObj:=Pastel;
        MoveC A_4_2_1,A_4_3,v100,z10,Marcador\WObj:=Pastel;
        MoveL A_4_4,v100,z10,Marcador\WObj:=Pastel;
        MoveC A_4_4_1,A_4_5,v100,z10,Marcador\WObj:=Pastel;
        MoveC A_4_5_1,A_4_6,v100,z10,Marcador\WObj:=Pastel;
        MoveC A_4_6_1,A_4_7,v100,z10,Marcador\WObj:=Pastel;
        MoveL A_4_8,v100,z10,Marcador\WObj:=Pastel;
        MoveL A_4_8_post,v100,z10,Marcador\WObj:=Pastel;
    ENDPROC
    PROC Path_N_2()
        MoveJ N_2_1_prev,v100,z10,Marcador\WObj:=Pastel;
        MoveL N_2_1,v100,z10,Marcador\WObj:=Pastel;
        MoveL N_2_2,v100,z10,Marcador\WObj:=Pastel;
        MoveL N_2_3,v100,z10,Marcador\WObj:=Pastel;
        MoveC N_2_3_1,N_2_4,v100,z10,Marcador\WObj:=Pastel;
        MoveC N_2_4_1,N_2_5,v100,z10,Marcador\WObj:=Pastel;
        MoveL N_2_5_post,v100,z10,Marcador\WObj:=Pastel;
    ENDPROC
    PROC Path_A_1()
        MoveJ A_1_1_prev,v100,z10,Marcador\WObj:=Pastel;
        MoveJ A_1_1,v100,z1,Marcador\WObj:=Pastel;
        MoveL A_1_2,v100,z1,Marcador\WObj:=Pastel;
        MoveL A_1_3,v100,z1,Marcador\WObj:=Pastel;
        MoveJ A_1_3_pos,v100,z1,Marcador\WObj:=Pastel;
        MoveJ A_1_4_prev,v100,z1,Marcador\WObj:=Pastel;
        MoveL A_1_4,v100,z1,Marcador\WObj:=Pastel;
        MoveL A_1_5,v100,z1,Marcador\WObj:=Pastel;
        MoveL A_1_5_post,v100,z10,Marcador\WObj:=Pastel;
    ENDPROC
    PROC Path_L()
        MoveJ L_1_prev,v100,z10,Marcador\WObj:=Pastel;
        MoveJ L_1,v100,z10,Marcador\WObj:=Pastel;
        MoveL L_2,v100,z10,Marcador\WObj:=Pastel;
    ENDPROC
    PROC Path_E()
        MoveJ E_1_prev,v100,z10,Marcador\WObj:=Pastel;
        MoveL E_1,v100,z10,Marcador\WObj:=Pastel;
        MoveL E_2,v100,z10,Marcador\WObj:=Pastel;
        MoveC E_2_1,E_3,v100,z10,Marcador\WObj:=Pastel;
        MoveC E_4,E_4_1,v100,z10,Marcador\WObj:=Pastel;
        MoveC E_4_2,E_5,v100,z10,Marcador\WObj:=Pastel;
        MoveL E_5_post,v100,z10,Marcador\WObj:=Pastel;
    ENDPROC
    PROC Path_JA()
        MoveJ JA_1_prev,v100,z10,Marcador\WObj:=Pastel;
        MoveL JA_1,v100,z10,Marcador\WObj:=Pastel;
        MoveL JA_2,v100,z10,Marcador\WObj:=Pastel;
        MoveL JA_3,v100,z10,Marcador\WObj:=Pastel;
        MoveC JA_3_1,JA_4,v100,z10,Marcador\WObj:=Pastel;
        MoveL JA_4_post,v100,z10,Marcador\WObj:=Pastel;    
    ENDPROC
    PROC Path_A_2()
        MoveL A_2_1_prev,v100,z10,Marcador\WObj:=Pastel;
        MoveL A_2_1,v100,z10,Marcador\WObj:=Pastel;
        MoveC A_2_1_2,A_2_1_3,v100,z10,Marcador\WObj:=Pastel;
        MoveC A_2_2_2,A_2_2,v100,z10,Marcador\WObj:=Pastel;
        MoveL A_2_3,v100,z10,Marcador\WObj:=Pastel;
        MoveC A_2_3_1,A_2_3_2,v100,z10,Marcador\WObj:=Pastel;
        MoveC A_2_3_3,A_2_3_4,v100,z10,Marcador\WObj:=Pastel;
        MoveL A_2_4,v100,z10,Marcador\WObj:=Pastel;
        MoveL A_2_5,v100,z10,Marcador\WObj:=Pastel;
        MoveL A_2_5_post,v100,z10,Marcador\WObj:=Pastel;
    ENDPROC
    PROC Path_N_1()
        MoveJ N_1_0,v100,z10,Marcador\WObj:=Pastel;
        MoveL N_1_1,v100,z10,Marcador\WObj:=Pastel;
        MoveL N_1_2,v100,z10,Marcador\WObj:=Pastel;
        MoveL N_1_3,v100,z10,Marcador\WObj:=Pastel;
        MoveC N_1_3_2,N_1_3_3,v100,z10,Marcador\WObj:=Pastel;
        MoveC N_1_3_4,N_1_4,v100,z10,Marcador\WObj:=Pastel;
        MoveL N_1_5,v100,z10,Marcador\WObj:=Pastel;
        MoveL N_1_5_post,v100,z10,Marcador\WObj:=Pastel;
    ENDPROC
    PROC Path_D()
        MoveL D_0,v100,z10,Marcador\WObj:=Pastel;
        MoveL D_1,v100,z10,Marcador\WObj:=Pastel;
        MoveC D_1_2,D_1_3,v100,z10,Marcador\WObj:=Pastel;
        MoveC D_1_4,D_1_5,v100,z10,Marcador\WObj:=Pastel;
        MoveC D_1_6,D_1_7,v100,z10,Marcador\WObj:=Pastel;
        MoveL D_2,v100,z1,Marcador\WObj:=Pastel;
        MoveL D_3,v100,z1,Marcador\WObj:=Pastel;
        MoveL D_4,v100,z1,Marcador\WObj:=Pastel;
        MoveL D_4_post,v100,z10,Marcador\WObj:=Pastel;
    ENDPROC
    PROC Path_Mantenimiento()
        MoveJ Target_Mantenimiento,v100,z10,Marcador\WObj:=wobj0;
    ENDPROC

ENDMODULE
```
