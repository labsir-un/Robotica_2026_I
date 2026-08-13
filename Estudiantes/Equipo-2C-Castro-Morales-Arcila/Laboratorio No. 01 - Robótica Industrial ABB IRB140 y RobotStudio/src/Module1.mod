MODULE Module1
    !PERS tooldata Herramienta:=[TRUE,[[66.25,-0.5,150.614],[0.965925826,0,0.258819045,0]],[1,[0,0,1],[1,0,0,0],0,0,0]];
    !TASK PERS wobjdata Workobject_1:=[FALSE,TRUE,"",[[-200,-16,-16],[1,0,0,0]],[[99.441586482,-660.070648704,644.432538512],[0.001790826,0.706567918,0.707641837,-0.001265687]]];     
   
    CONST robtarget Target_Mant:=[[1546.269135318,330.78861341,-92.400811518],[0.016971313,-0.578893265,-0.003030547,-0.815221061],[1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_10:=[[169,1,-50],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_20:=[[169,1,-2],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_30:=[[300,300,-50],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_40:=[[300,600,-50],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_50:=[[400,750,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_Home:=[[694.848073696,884.059706691,82.569822298],[0.685261568,-0.179316211,-0.176654625,-0.683414533],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_60:=[[50,190,-19.2],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_70:=[[50,190,0.8],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_80:=[[10,190,0.8],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_Inicio:=[[674.848072279,705.126370613,70.218390264],[0.683993026,-0.184095793,-0.181421379,-0.682164616],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_120:=[[250,500,0],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_90:=[[169,1,-50],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_110:=[[200,300,-50],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_100:=[[169,1,0],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_150:=[[50,97.5,-17.3],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_130:=[[10,97.5,2.7],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_140:=[[50,97.5,2.7],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_160:=[[13.75,190,0.8],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_170:=[[11.098,188.902,0.8],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_180:=[[10,186.25,0.8],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_190:=[[10,178.75,0.8],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_200:=[[11.098,176.098,0.8],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_210:=[[13.75,175,0.8],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_220:=[[26.25,175,0.8],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_230:=[[28.902,176.098,0.8],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_240:=[[30,178.75,0.8],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_250:=[[30,186.25,0.8],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_260:=[[28.902,188.902,0.8],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_270:=[[26.25,190,0.8],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_280:=[[26.25,190,-19.2],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_290:=[[50,155,-19.2],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_300:=[[50,155,0.8],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_310:=[[25,155,0.8],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_320:=[[33.75,155,0.8],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_330:=[[31.098,156.098,0.8],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_340:=[[30,158.75,0.8],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_350:=[[30,166.25,0.8],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_360:=[[31.098,168.902,0.8],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_370:=[[33.75,170,0.8],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_380:=[[46.25,170,0.8],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_390:=[[48.902,168.902,0.8],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_400:=[[50,166.25,0.8],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_410:=[[50,158.75,0.8],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_420:=[[48.902,156.098,0.8],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_430:=[[46.25,155,0.8],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_440:=[[46.25,155,-19.2],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_450:=[[50,150,-19.2],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_460:=[[50,150,0.8],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_470:=[[10,150,0.8],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_480:=[[33.75,150,0.8],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_490:=[[31.098,148.902,0.8],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_500:=[[30,146.25,0.8],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_510:=[[30,138.75,0.8],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_520:=[[31.098,136.098,0.8],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_530:=[[33.75,135,0.8],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_540:=[[46.25,135,0.8],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_550:=[[48.902,136.098,0.8],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_560:=[[50,138.75,0.8],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_570:=[[50,146.25,0.8],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_580:=[[48.902,148.902,0.8],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_590:=[[46.25,150,0.8],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_600:=[[46.25,150,-19.2],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_630:=[[10,130,0.8],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_610:=[[50,130,-19.2],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_620:=[[50,130,0.8],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_760:=[[48.902,123.902,-2.2],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_640:=[[46.25,125,-19.2],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_650:=[[46.25,125,0.8],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_660:=[[33.75,125,0.8],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_670:=[[31.098,123.902,0.8],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_680:=[[30,121.25,0.8],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_690:=[[30,113.75,0.8],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_700:=[[31.098,111.098,0.8],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_710:=[[33.75,110,0.8],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_720:=[[46.25,110,0.8],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_730:=[[48.902,111.098,0.8],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_740:=[[50,113.75,0.8],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_750:=[[50,121.25,0.8],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_770:=[[30,90,2.7],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_780:=[[10,82.5,2.7],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_790:=[[50,82.5,2.7],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_800:=[[50,82.5,-17.3],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_810:=[[50,62.5,-17.3],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_820:=[[50,62.5,2.7],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_830:=[[25,62.5,2.7],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_840:=[[33.75,62.5,2.7],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_850:=[[31.098,63.598,2.7],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_860:=[[30,66.25,2.7],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_870:=[[30,73.75,2.7],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_880:=[[31.098,76.402,2.7],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_890:=[[33.75,77.5,2.7],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_900:=[[46.25,77.5,2.7],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_910:=[[48.902,76.402,2.7],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_920:=[[50,73.75,2.7],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_930:=[[50,66.25,2.7],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_940:=[[48.902,63.598,2.7],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_950:=[[46.25,62.5,2.7],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_960:=[[46.25,62.5,-17.3],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_970:=[[50,57.5,-17.3],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_980:=[[50,57.5,2.7],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_990:=[[25,57.5,2.7],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1000:=[[32.5,57.5,2.7],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1010:=[[30.732,56.768,2.7],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1020:=[[30,55,2.7],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1030:=[[30,52.5,2.7],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1040:=[[30,52.5,-17.3],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1180:=[[46.25,32.5,-17.3],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1050:=[[33.75,32.5,-17.3],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1060:=[[33.75,32.5,2.7],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1070:=[[31.098,33.598,2.7],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1080:=[[30,36.25,2.7],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1090:=[[30,43.75,2.7],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1100:=[[31.098,46.402,2.7],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1110:=[[33.75,47.5,2.7],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1120:=[[46.25,47.5,2.7],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1130:=[[48.902,46.402,2.7],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1140:=[[50,43.75,2.7],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1150:=[[50,36.25,2.7],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1160:=[[48.902,33.598,2.7],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1170:=[[46.25,32.5,2.7],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1330:=[[46.25,27.5,-16.7],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1190:=[[46.25,27.5,-16.7],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1200:=[[46.25,27.5,3.3],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1210:=[[33.75,27.5,3.3],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1220:=[[31.098,26.402,3.3],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1230:=[[30,23.75,3.3],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1240:=[[30,16.25,3.3],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1250:=[[31.098,13.598,3.3],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1260:=[[33.75,12.5,3.3],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1270:=[[46.25,12.5,3.3],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1280:=[[48.902,13.598,3.3],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1290:=[[50,16.25,3.3],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1300:=[[50,23.75,3.3],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1310:=[[48.902,26.402,3.3],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1320:=[[46.25,27.5,3.3],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1440:=[[95,143.75,-20],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1340:=[[95,143.75,-20],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1350:=[[95,143.75,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1360:=[[55,143.75,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1370:=[[55,132.5,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1380:=[[56.098,129.848,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1390:=[[58.75,128.75,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1400:=[[91.25,128.75,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1410:=[[93.902,129.848,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1420:=[[95,132.5,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1430:=[[95,143.75,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1450:=[[95,108.75,-20],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1460:=[[95,108.75,0],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1470:=[[70,108.75,0],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1480:=[[78.75,108.75,0],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1490:=[[76.098,109.848,0],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1500:=[[75,112.5,0],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1510:=[[75,120,0],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1520:=[[76.098,122.652,0],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1530:=[[78.75,123.75,0],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1540:=[[91.25,123.75,0],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1550:=[[93.902,122.652,0],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1560:=[[95,120,0],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1570:=[[95,112.5,0],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1580:=[[93.902,109.848,0],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1590:=[[91.25,108.75,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1600:=[[91.25,108.75,-20],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1610:=[[95,103.75,-20],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1620:=[[95,103.75,0],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1630:=[[75,103.75,0],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1640:=[[78.75,103.75,0],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1650:=[[76.098,102.652,0],[1,0,0,0],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1660:=[[75,100,0],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1670:=[[75,92.5,0],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1680:=[[76.098,89.848,0],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1690:=[[78.75,88.75,0],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1700:=[[95,88.75,0],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1710:=[[95,88.75,-20],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1720:=[[95,83.75,-20],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1730:=[[95,83.75,0],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1740:=[[75,83.75,0],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1750:=[[95,83.75,0],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1760:=[[95,83.75,-20],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1940:=[[85,78.75,-20],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1770:=[[91.25,63.75,-20],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1780:=[[91.25,63.75,0],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1790:=[[93.902,64.848,0],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1800:=[[95,67.5,0],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1810:=[[95,75,0],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1820:=[[93.902,77.652,0],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1830:=[[91.25,78.75,0],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1840:=[[78.75,78.75,0],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1850:=[[76.098,77.652,0],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1860:=[[75,75,0],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1870:=[[75,67.5,0],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1880:=[[76.098,64.848,0],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1890:=[[78.75,63.75,0],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1900:=[[81.25,63.75,0],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1910:=[[83.902,64.848,0],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1920:=[[85,67.5,0],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1930:=[[85,78.75,0],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1950:=[[95,58.75,-20],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1960:=[[95,58.75,0],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1970:=[[55,58.75,0],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1980:=[[95,58.75,0],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_1990:=[[95,58.75,-20],[1,0,0,0],[-2,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_2000:=[[151.25,102.5,-21.3],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_2010:=[[151.25,102.5,-1.3],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_2020:=[[151.25,125.625,-1.3],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_2030:=[[105,102.5,-1.3],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_2040:=[[151.25,79.375,-1.3],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_2050:=[[151.25,102.5,-1.3],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_2060:=[[136.958,116.792,-1.3],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_2070:=[[122.666,102.5,-1.3],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_2080:=[[151.25,102.5,-1.3],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_2090:=[[136.958,88.208,-1.3],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_2100:=[[122.666,102.5,-1.3],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_2110:=[[105,102.5,-1.3],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_2120:=[[105,102.5,-21.3],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_Mantenimiento:=[[1395.476689519,103.276551126,-144.201335043],[0.000839993,-0.539120967,-0.000094816,-0.842227919],[1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_2130:=[[1113.946312594,517.178856745,68.181103053],[0.35801856,-0.242222444,-0.094746507,-0.896757547],[0,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_2140:=[[1399.342292108,180.658370976,-180.11158222],[0.041257006,-0.651549348,-0.03473117,-0.756686892],[0,-1,0,1],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    !PERS tooldata Herramienta:=[TRUE,[[66.25,-0.5,150.614],[0.965925826,0,0.258819045,0]],[1,[0,0,1],[1,0,0,0],0,0,0]];
    !TASK PERS wobjdata Workobject_1:=[FALSE,TRUE,"",[[-200,-45,-12],[1,0,0,0]],[[-80.5211,-680.383,635.386],[0.00677729,0.695963,0.718037,0.00357443]]];
    !TASK PERS wobjdata Workobject_2:=[FALSE,TRUE,"",[[-100,0,0],[1,0,0,0]],[[-80.5211,-680.383,635.386],[0.00677729,0.695963,0.718037,0.00357443]]];
   
    
    

    PROC main()
        
        WHILE TRUE DO
            RESET DO_01;
            RESET DO_02;
            RESET DO_03;
            
            IF DI_01 = 1 THEN
                SET DO_01;
                
                SET BWD_Conveyor;
                
                SET Salida_SC;
                
                WaitTime 7;
                RESET BWD_Conveyor;
                WaitTime 5;
                
                Path_Aprox_1_1;
                Path_Pablo;
                Path_Marco;
                Path_Daniel;
                Path_Figura;
                Path_Aprox_1_2;
                
                WaitTime 5;
                SET BWD_Conveyor;
                SET Salida_Final;
                WaitTime 2;
                RESET BWD_Conveyor;
                RESET DO_01;
                WaitTime 5;
                SET Regreso;
            ENDIF
            
            IF DI_02=1 THEN
                SET DO_02;
                Path_Mantenimiento;

            ENDIF
            
            
            IF DI_03 = 1 THEN
                SET DO_03;
                Path_Aprox_1_1;
                WaitTime 30;
                Path_Aprox_1;
                WaitTime 5;
                Path_Aprox_1_2;
                SET FWD_Conveyor;
                
                SET Salida_Fin;
                
                WaitTime 7;
                RESET FWD_Conveyor;
                RESET DO_03;
            ENDIF
            
        ENDWHILE
 
    ENDPROC

    PROC Path_Aprox_1()
        MoveL Target_90,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_60,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_80,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_1190,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_1250,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_90,v100,z5,Herramienta\WObj:=Workobject_1;
    ENDPROC
    PROC Path_Aprox_1_1()
        MoveL Target_Inicio,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_120,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_110,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_90,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_100,v100,z5,Herramienta\WObj:=Workobject_1;
        
    ENDPROC
    
        PROC Path_Aprox_1_2()
        MoveL Target_90,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_110,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_120,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_Inicio,v100,z5,Herramienta\WObj:=Workobject_1;
        
    ENDPROC
    PROC Path_Pablo()
!!! P
        MoveL Target_60,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_70,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_80,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_160,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveC Target_170,Target_180,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_190,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveC Target_200,Target_210,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_220,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveC Target_230,Target_240,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_250,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveC Target_260,Target_270,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_280,v100,z5,Herramienta\WObj:=Workobject_1;
 !!!! A      
        MoveL Target_290,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_300,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_310,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_320,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveC Target_330,Target_340,v100,z5,Herramienta\WObj:=Workobject_1;
        
        MoveL Target_350,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveC Target_360,Target_370,v100,z5,Herramienta\WObj:=Workobject_1;

        MoveL Target_380,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveC Target_390,Target_400,v100,z5,Herramienta\WObj:=Workobject_1;
        
        MoveL Target_410,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveC Target_420,Target_430,v100,z5,Herramienta\WObj:=Workobject_1;
        
        MoveL Target_440,v100,z5,Herramienta\WObj:=Workobject_1;
!!! B       
        MoveL Target_450,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_460,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_470,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_480,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveC Target_490,Target_500,v100,z5,Herramienta\WObj:=Workobject_1;
        
        MoveL Target_510,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveC Target_520,Target_530,v100,z5,Herramienta\WObj:=Workobject_1;
        
        MoveL Target_540,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveC Target_550,Target_560,v100,z5,Herramienta\WObj:=Workobject_1;
       
        MoveL Target_570,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveC Target_580,Target_590,v100,z5,Herramienta\WObj:=Workobject_1;
        
        MoveL Target_600,v100,z5,Herramienta\WObj:=Workobject_1;
!!! L       
        MoveL Target_610,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_620,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_630,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_620,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_610,v100,z5,Herramienta\WObj:=Workobject_1;
!!! O       
        MoveL Target_640,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_650,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_660,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveC Target_670,Target_680,v100,z5,Herramienta\WObj:=Workobject_1;
        
        MoveL Target_690,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveC Target_700,Target_710,v100,z5,Herramienta\WObj:=Workobject_1;
        
        MoveL Target_720,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveC Target_730,Target_740,v100,z5,Herramienta\WObj:=Workobject_1;
       
        MoveL Target_750,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveC Target_760,Target_650,v100,z5,Herramienta\WObj:=Workobject_1;
        
        MoveL Target_640,v100,z5,Herramienta\WObj:=Workobject_1;
        

    ENDPROC
    PROC Path_Marco()
!!! M
        MoveL Target_150,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_140,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_130,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_770,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_780,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_790,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_800,v100,z5,Herramienta\WObj:=Workobject_1;
!!! A        
        MoveL Target_810,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_820,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_830,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_840,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveC Target_850,Target_860,v100,z5,Herramienta\WObj:=Workobject_1;
        
        MoveL Target_870,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveC Target_880,Target_890,v100,z5,Herramienta\WObj:=Workobject_1;
        
        MoveL Target_900,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveC Target_910,Target_920,v100,z5,Herramienta\WObj:=Workobject_1;
        
        MoveL Target_930,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveC Target_940,Target_950,v100,z5,Herramienta\WObj:=Workobject_1;
        
        MoveL Target_960,v100,z5,Herramienta\WObj:=Workobject_1;
!!! R
        MoveL Target_970,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_980,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_990,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_1000,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveC Target_1010,Target_1020,v100,z5,Herramienta\WObj:=Workobject_1;
        
        MoveL Target_1030,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_1040,v100,z5,Herramienta\WObj:=Workobject_1;
!!! C
        
        MoveL Target_1050,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_1060,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveC Target_1070,Target_1080,v100,z5,Herramienta\WObj:=Workobject_1;
        
        MoveL Target_1090,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveC Target_1100,Target_1110,v100,z5,Herramienta\WObj:=Workobject_1;
        
        MoveL Target_1120,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveC Target_1130,Target_1140,v100,z5,Herramienta\WObj:=Workobject_1;
        
        MoveL Target_1150,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveC Target_1160,Target_1170,v100,z5,Herramienta\WObj:=Workobject_1;
       
        MoveL Target_1180,v100,z5,Herramienta\WObj:=Workobject_1;
!!! O        
        MoveL Target_1190,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_1200,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_1210,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveC Target_1220,Target_1230,v100,z5,Herramienta\WObj:=Workobject_1;
        
        MoveL Target_1240,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveC Target_1250,Target_1260,v100,z5,Herramienta\WObj:=Workobject_1;
        
        MoveL Target_1270,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveC Target_1280,Target_1290,v100,z5,Herramienta\WObj:=Workobject_1;
        
        MoveL Target_1300,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveC Target_1310,Target_1320,v100,z5,Herramienta\WObj:=Workobject_1;
        
        MoveL Target_1330,v100,z5,Herramienta\WObj:=Workobject_1;
    ENDPROC
    PROC Path_Daniel()
!!! D
        MoveL Target_1340,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_1350,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_1360,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_1370,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveC Target_1380,Target_1390,v100,z5,Herramienta\WObj:=Workobject_1;
        
        MoveL Target_1400,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveC Target_1410,Target_1420,v100,z5,Herramienta\WObj:=Workobject_1;
        
        MoveL Target_1430,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_1440,v100,z5,Herramienta\WObj:=Workobject_1;
!!! A
        MoveL Target_1450,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_1460,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_1470,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_1480,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveC Target_1490,Target_1500,v100,z5,Herramienta\WObj:=Workobject_1;
        
        MoveL Target_1510,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveC Target_1520,Target_1530,v100,z5,Herramienta\WObj:=Workobject_1;
        
        MoveL Target_1540,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveC Target_1550,Target_1560,v100,z5,Herramienta\WObj:=Workobject_1;
        
        MoveL Target_1570,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveC Target_1580,Target_1590,v100,z5,Herramienta\WObj:=Workobject_1;
        
        MoveL Target_1600,v100,z5,Herramienta\WObj:=Workobject_1;
!!! N
        MoveL Target_1610,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_1620,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_1630,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_1640,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveC Target_1650,Target_1660,v100,z5,Herramienta\WObj:=Workobject_1;
        
        MoveL Target_1670,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveC Target_1680,Target_1690,v100,z5,Herramienta\WObj:=Workobject_1;
        
        MoveL Target_1700,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_1710,v100,z5,Herramienta\WObj:=Workobject_1;
!!! I
        MoveL Target_1720,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_1730,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_1740,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_1750,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_1760,v100,z5,Herramienta\WObj:=Workobject_1;
!!! E       
        MoveL Target_1770,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_1780,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveC Target_1790,Target_1800,v100,z5,Herramienta\WObj:=Workobject_1;
        
        MoveL Target_1810,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveC Target_1820,Target_1830,v100,z5,Herramienta\WObj:=Workobject_1;
        
        MoveL Target_1840,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveC Target_1850,Target_1860,v100,z5,Herramienta\WObj:=Workobject_1;
        
        MoveL Target_1870,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveC Target_1880,Target_1890,v100,z5,Herramienta\WObj:=Workobject_1;
        
        MoveL Target_1900,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveC Target_1910,Target_1920,v100,z5,Herramienta\WObj:=Workobject_1;
        
        MoveL Target_1930,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_1940,v100,z5,Herramienta\WObj:=Workobject_1;
!!! L
        MoveL Target_1950,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_1960,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_1970,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_1980,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_1990,v100,z5,Herramienta\WObj:=Workobject_1;
    ENDPROC
    PROC Path_Figura()
        MoveL Target_2000,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_2010,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_2020,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_2030,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_2040,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_2050,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveC Target_2060,Target_2070,v100,z5,Herramienta\WObj:=Workobject_1;
        
        MoveL Target_2080,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveC Target_2090,Target_2100,v100,z5,Herramienta\WObj:=Workobject_1;
        
        MoveL Target_2110,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_2120,v100,z5,Herramienta\WObj:=Workobject_1;
    ENDPROC
    PROC Path_Mantenimiento()
        MoveL Target_Inicio,v100,z5,Herramienta\WObj:=Workobject_1;
        MoveL Target_Mantenimiento,v100,z5,Herramienta\WObj:=Workobject_1;
    ENDPROC



ENDMODULE