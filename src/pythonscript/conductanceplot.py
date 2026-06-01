import re
import matplotlib.pyplot as plt

runs = {

"1ccccc":"""
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001406293
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001312540
> drain
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001187536
Teensy: Current conductance: 0.000000001406293
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001250038
Teensy: Current conductance: 0.000000001250038
Teensy: Current conductance: 0.000000001218787
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001250038
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001218787
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001250038
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001218787
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001406293
Teensy: Current conductance: 0.000000001250038
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001406293
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001250038
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001562548
Teensy: Current conductance: 0.000000001937559
Teensy: Current conductance: 0.000000002375073
Teensy: Current conductance: 0.000000003656362
Teensy: Current conductance: 0.000000004687643
Teensy: Current conductance: 0.000000005781426
Teensy: Current conductance: 0.000000007375225
Teensy: Current conductance: 0.000000009094028
Teensy: Current conductance: 0.000000010687827
Teensy: Current conductance: 0.000000012312876
Teensy: Current conductance: 0.000000013719170
Teensy: Current conductance: 0.000000015656731
Teensy: Current conductance: 0.000000017063021
Teensy: Current conductance: 0.000000018625569
Teensy: Current conductance: 0.000000021031894
Teensy: Current conductance: 0.000000023031953
Teensy: Current conductance: 0.000000025032016
Teensy: Current conductance: 0.000000027094579
Teensy: Current conductance: 0.000000028500871
Teensy: Current conductance: 0.000000030563434
Teensy: Current conductance: 0.000000032657251
Teensy: Current conductance: 0.000000034657312
Teensy: Current conductance: 0.000000036626119
Teensy: Current conductance: 0.000000038563680
Teensy: Current conductance: 0.000000041063753
Teensy: Current conductance: 0.000000043438831
Teensy: Current conductance: 0.000000044876373
Teensy: Current conductance: 0.000000047032689
Teensy: Current conductance: 0.000000049532762
Teensy: Current conductance: 0.000000050907804
Teensy: Current conductance: 0.000000053501637
Teensy: Current conductance: 0.000000055189187
Teensy: Current conductance: 0.000000057157997
Teensy: Current conductance: 0.000000059189308
Teensy: Current conductance: 0.000000060345592
Teensy: Current conductance: 0.000000062439412
Teensy: Current conductance: 0.000000063845704
Teensy: Current conductance: 0.000000065376994
Teensy: Current conductance: 0.000000066564539
Teensy: Current conductance: 0.000000067252053
Teensy: Current conductance: 0.000000068658345
Teensy: Current conductance: 0.000000069220867
Teensy: Current conductance: 0.000000069752133
Teensy: Current conductance: 0.000000069814639
Teensy: Current conductance: 0.000000070158393
Teensy: Current conductance: 0.000000069752133
Teensy: Current conductance: 0.000000069564628
Teensy: Current conductance: 0.000000068595845
Teensy: Current conductance: 0.000000067845818
Teensy: Current conductance: 0.000000066752037
Teensy: Current conductance: 0.000000065283238
Teensy: Current conductance: 0.000000063501936
Teensy: Current conductance: 0.000000061658135
Teensy: Current conductance: 0.000000059470569
Teensy: Current conductance: 0.000000057970524
Teensy: Current conductance: 0.000000055001685
Teensy: Current conductance: 0.000000052814116
Teensy: Current conductance: 0.000000050032778
Teensy: Current conductance: 0.000000047251444
Teensy: Current conductance: 0.000000045470138
Teensy: Current conductance: 0.000000042595051
Teensy: Current conductance: 0.000000040594990
Teensy: Current conductance: 0.000000038094914
Teensy: Current conductance: 0.000000036532366
Teensy: Current conductance: 0.000000034344801
Teensy: Current conductance: 0.000000032344740
Teensy: Current conductance: 0.000000031344708
Teensy: Current conductance: 0.000000029344648
Teensy: Current conductance: 0.000000028469620
Teensy: Current conductance: 0.000000027125829
Teensy: Current conductance: 0.000000026063297
Teensy: Current conductance: 0.000000025438277
Teensy: Current conductance: 0.000000024313243
Teensy: Current conductance: 0.000000023719476
Teensy: Current conductance: 0.000000022531937
Teensy: Current conductance: 0.000000021906919
Teensy: Current conductance: 0.000000021656913
Teensy: Current conductance: 0.000000021500657
Teensy: Current conductance: 0.000000021000643
Teensy: Current conductance: 0.000000020875639
Teensy: Current conductance: 0.000000020063114
> drain
Teensy: Current conductance: 0.000000020156866
Teensy: Current conductance: 0.000000019750605
Teensy: Current conductance: 0.000000019594349
Teensy: Current conductance: 0.000000019500595
Teensy: Current conductance: 0.000000019313090
Teensy: Current conductance: 0.000000019063082
Teensy: Current conductance: 0.000000018813076
Teensy: Current conductance: 0.000000018750573
Teensy: Current conductance: 0.000000018813076
Teensy: Current conductance: 0.000000018719323
Teensy: Current conductance: 0.000000018531818
""",
"1cccccc":"""
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001218787
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001375042
> drain
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001250038
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001250038
Teensy: Current conductance: 0.000000001187536
Teensy: Current conductance: 0.000000001187536
Teensy: Current conductance: 0.000000001218787
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001187536
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001218787
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001218787
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001250038
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001437544
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001531297
Teensy: Current conductance: 0.000000001750053
Teensy: Current conductance: 0.000000002312571
Teensy: Current conductance: 0.000000003437605
Teensy: Current conductance: 0.000000004125126
Teensy: Current conductance: 0.000000005968932
Teensy: Current conductance: 0.000000007093967
Teensy: Current conductance: 0.000000008531511
Teensy: Current conductance: 0.000000009687795
Teensy: Current conductance: 0.000000011844111
Teensy: Current conductance: 0.000000013219154
Teensy: Current conductance: 0.000000015031711
Teensy: Current conductance: 0.000000016531756
Teensy: Current conductance: 0.000000018313060
Teensy: Current conductance: 0.000000020375623
Teensy: Current conductance: 0.000000022281931
Teensy: Current conductance: 0.000000024000732
Teensy: Current conductance: 0.000000025657034
Teensy: Current conductance: 0.000000027907104
Teensy: Current conductance: 0.000000029969666
Teensy: Current conductance: 0.000000031844724
Teensy: Current conductance: 0.000000033532277
Teensy: Current conductance: 0.000000036001101
Teensy: Current conductance: 0.000000037844906
Teensy: Current conductance: 0.000000039844966
Teensy: Current conductance: 0.000000042220041
Teensy: Current conductance: 0.000000044345104
Teensy: Current conductance: 0.000000046282665
Teensy: Current conductance: 0.000000048345228
Teensy: Current conductance: 0.000000050407788
Teensy: Current conductance: 0.000000052439106
Teensy: Current conductance: 0.000000054626671
Teensy: Current conductance: 0.000000056157965
Teensy: Current conductance: 0.000000058626789
Teensy: Current conductance: 0.000000060001838
Teensy: Current conductance: 0.000000062001895
Teensy: Current conductance: 0.000000063501936
Teensy: Current conductance: 0.000000064814479
Teensy: Current conductance: 0.000000066877043
Teensy: Current conductance: 0.000000068002080
Teensy: Current conductance: 0.000000068908356
Teensy: Current conductance: 0.000000069970888
Teensy: Current conductance: 0.000000070220899
Teensy: Current conductance: 0.000000071283431
Teensy: Current conductance: 0.000000071814696
Teensy: Current conductance: 0.000000072002202
Teensy: Current conductance: 0.000000071783447
Teensy: Current conductance: 0.000000071127168
Teensy: Current conductance: 0.000000070377148
Teensy: Current conductance: 0.000000069783383
Teensy: Current conductance: 0.000000068252085
Teensy: Current conductance: 0.000000067127047
Teensy: Current conductance: 0.000000064908235
Teensy: Current conductance: 0.000000063595692
Teensy: Current conductance: 0.000000061314374
Teensy: Current conductance: 0.000000059314313
Teensy: Current conductance: 0.000000056657981
Teensy: Current conductance: 0.000000054595418
Teensy: Current conductance: 0.000000052407849
Teensy: Current conductance: 0.000000049814023
Teensy: Current conductance: 0.000000047220194
Teensy: Current conductance: 0.000000044657614
Teensy: Current conductance: 0.000000042126288
Teensy: Current conductance: 0.000000040626244
Teensy: Current conductance: 0.000000038313672
Teensy: Current conductance: 0.000000035938598
Teensy: Current conductance: 0.000000033907288
Teensy: Current conductance: 0.000000032969758
Teensy: Current conductance: 0.000000031313462
Teensy: Current conductance: 0.000000030094672
Teensy: Current conductance: 0.000000028000855
Teensy: Current conductance: 0.000000027250833
Teensy: Current conductance: 0.000000026625814
Teensy: Current conductance: 0.000000025563281
Teensy: Current conductance: 0.000000024532000
Teensy: Current conductance: 0.000000024625752
Teensy: Current conductance: 0.000000023406963
Teensy: Current conductance: 0.000000022813197
Teensy: Current conductance: 0.000000022406933
Teensy: Current conductance: 0.000000022000672
Teensy: Current conductance: 0.000000021188148
Teensy: Current conductance: 0.000000021313152
Teensy: Current conductance: 0.000000020656881
Teensy: Current conductance: 0.000000020531877
Teensy: Current conductance: 0.000000020625631
Teensy: Current conductance: 0.000000020594380
Teensy: Current conductance: 0.000000020500627
Teensy: Current conductance: 0.000000019813106
Teensy: Current conductance: 0.000000020031862
Teensy: Current conductance: 0.000000019938110
Teensy: Current conductance: 0.000000019469345
Teensy: Current conductance: 0.000000019563100
Teensy: Current conductance: 0.000000019250589
""",
"1ccccccc":"""
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001406293
Teensy: Current conductance: 0.000000001406293
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001406293
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001250038
> drain
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001218787
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001218787
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001218787
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001250038
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001156285
Teensy: Current conductance: 0.000000001218787
Teensy: Current conductance: 0.000000001218787
Teensy: Current conductance: 0.000000001250038
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001218787
Teensy: Current conductance: 0.000000001218787
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001250038
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001593799
Teensy: Current conductance: 0.000000001718803
Teensy: Current conductance: 0.000000002250069
Teensy: Current conductance: 0.000000003093845
Teensy: Current conductance: 0.000000004937651
Teensy: Current conductance: 0.000000005906430
Teensy: Current conductance: 0.000000006750206
Teensy: Current conductance: 0.000000008312753
Teensy: Current conductance: 0.000000009906553
Teensy: Current conductance: 0.000000011250344
Teensy: Current conductance: 0.000000013312907
Teensy: Current conductance: 0.000000015000460
Teensy: Current conductance: 0.000000016719261
Teensy: Current conductance: 0.000000018188056
Teensy: Current conductance: 0.000000019875609
Teensy: Current conductance: 0.000000021781915
Teensy: Current conductance: 0.000000023469468
Teensy: Current conductance: 0.000000025532030
Teensy: Current conductance: 0.000000027375838
Teensy: Current conductance: 0.000000029969666
Teensy: Current conductance: 0.000000031782221
Teensy: Current conductance: 0.000000033376018
Teensy: Current conductance: 0.000000036126103
Teensy: Current conductance: 0.000000038001161
Teensy: Current conductance: 0.000000040157477
Teensy: Current conductance: 0.000000042157538
Teensy: Current conductance: 0.000000043970093
Teensy: Current conductance: 0.000000046313914
Teensy: Current conductance: 0.000000048188973
Teensy: Current conductance: 0.000000050251536
Teensy: Current conductance: 0.000000052282846
Teensy: Current conductance: 0.000000053845394
Teensy: Current conductance: 0.000000056126716
Teensy: Current conductance: 0.000000058314281
Teensy: Current conductance: 0.000000060033088
Teensy: Current conductance: 0.000000062220650
Teensy: Current conductance: 0.000000063751948
Teensy: Current conductance: 0.000000064845736
Teensy: Current conductance: 0.000000066752037
Teensy: Current conductance: 0.000000067845818
Teensy: Current conductance: 0.000000069439622
Teensy: Current conductance: 0.000000069939638
Teensy: Current conductance: 0.000000070658409
Teensy: Current conductance: 0.000000071502186
Teensy: Current conductance: 0.000000072220956
Teensy: Current conductance: 0.000000072658473
Teensy: Current conductance: 0.000000072939734
Teensy: Current conductance: 0.000000072408469
Teensy: Current conductance: 0.000000071533435
Teensy: Current conductance: 0.000000070877164
Teensy: Current conductance: 0.000000070658409
Teensy: Current conductance: 0.000000068970856
Teensy: Current conductance: 0.000000068470840
Teensy: Current conductance: 0.000000066220778
Teensy: Current conductance: 0.000000064251957
Teensy: Current conductance: 0.000000062595660
Teensy: Current conductance: 0.000000059720577
Teensy: Current conductance: 0.000000057814269
Teensy: Current conductance: 0.000000055032931
Teensy: Current conductance: 0.000000053032867
Teensy: Current conductance: 0.000000050439041
Teensy: Current conductance: 0.000000047813963
Teensy: Current conductance: 0.000000046095160
Teensy: Current conductance: 0.000000043126320
Teensy: Current conductance: 0.000000041438767
Teensy: Current conductance: 0.000000039282451
Teensy: Current conductance: 0.000000037438646
Teensy: Current conductance: 0.000000035376083
Teensy: Current conductance: 0.000000033813532
Teensy: Current conductance: 0.000000032219734
Teensy: Current conductance: 0.000000030594684
Teensy: Current conductance: 0.000000029657157
Teensy: Current conductance: 0.000000028625875
Teensy: Current conductance: 0.000000027438340
Teensy: Current conductance: 0.000000026500810
Teensy: Current conductance: 0.000000025907042
Teensy: Current conductance: 0.000000025375776
Teensy: Current conductance: 0.000000024375744
Teensy: Current conductance: 0.000000024188239
Teensy: Current conductance: 0.000000023250710
Teensy: Current conductance: 0.000000023156957
Teensy: Current conductance: 0.000000023063205
Teensy: Current conductance: 0.000000022156927
Teensy: Current conductance: 0.000000021906919
Teensy: Current conductance: 0.000000021531909
Teensy: Current conductance: 0.000000021563160
Teensy: Current conductance: 0.000000021500657
Teensy: Current conductance: 0.000000020875639
Teensy: Current conductance: 0.000000021156898
Teensy: Current conductance: 0.000000020750635
Teensy: Current conductance: 0.000000020500627
Teensy: Current conductance: 0.000000020469376
Teensy: Current conductance: 0.000000019969361
Teensy: Current conductance: 0.000000019938110
""",
"1cccccccc":"""
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001250038
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001343791
> drain
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001218787
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001250038
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001218787
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001250038
Teensy: Current conductance: 0.000000001250038
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001218787
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001250038
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001406293
Teensy: Current conductance: 0.000000001687552
Teensy: Current conductance: 0.000000002343822
Teensy: Current conductance: 0.000000002843837
Teensy: Current conductance: 0.000000003781366
Teensy: Current conductance: 0.000000004750145
Teensy: Current conductance: 0.000000007000214
Teensy: Current conductance: 0.000000008250251
Teensy: Current conductance: 0.000000009906553
Teensy: Current conductance: 0.000000011781609
Teensy: Current conductance: 0.000000012406630
Teensy: Current conductance: 0.000000014062929
Teensy: Current conductance: 0.000000015969238
Teensy: Current conductance: 0.000000018125554
Teensy: Current conductance: 0.000000019750605
Teensy: Current conductance: 0.000000021469408
Teensy: Current conductance: 0.000000023563219
Teensy: Current conductance: 0.000000024907012
Teensy: Current conductance: 0.000000027344587
Teensy: Current conductance: 0.000000028750877
Teensy: Current conductance: 0.000000030469682
Teensy: Current conductance: 0.000000032532245
Teensy: Current conductance: 0.000000035063572
Teensy: Current conductance: 0.000000036876127
Teensy: Current conductance: 0.000000039376207
Teensy: Current conductance: 0.000000041438767
Teensy: Current conductance: 0.000000043595083
Teensy: Current conductance: 0.000000045563890
Teensy: Current conductance: 0.000000048126470
Teensy: Current conductance: 0.000000049595268
Teensy: Current conductance: 0.000000051970339
Teensy: Current conductance: 0.000000054657921
Teensy: Current conductance: 0.000000056001710
Teensy: Current conductance: 0.000000057845519
Teensy: Current conductance: 0.000000060345592
Teensy: Current conductance: 0.000000061564386
Teensy: Current conductance: 0.000000063189432
Teensy: Current conductance: 0.000000064595731
Teensy: Current conductance: 0.000000066377027
Teensy: Current conductance: 0.000000067783326
Teensy: Current conductance: 0.000000069345866
Teensy: Current conductance: 0.000000069908381
Teensy: Current conductance: 0.000000071783447
Teensy: Current conductance: 0.000000072439718
Teensy: Current conductance: 0.000000072939734
Teensy: Current conductance: 0.000000073627255
Teensy: Current conductance: 0.000000073127239
Teensy: Current conductance: 0.000000073002234
Teensy: Current conductance: 0.000000072845971
Teensy: Current conductance: 0.000000072314712
Teensy: Current conductance: 0.000000071533435
Teensy: Current conductance: 0.000000070627152
Teensy: Current conductance: 0.000000069158361
Teensy: Current conductance: 0.000000067627063
Teensy: Current conductance: 0.000000066189521
Teensy: Current conductance: 0.000000063595692
Teensy: Current conductance: 0.000000061658135
Teensy: Current conductance: 0.000000059251811
Teensy: Current conductance: 0.000000057189244
Teensy: Current conductance: 0.000000054876679
Teensy: Current conductance: 0.000000051907836
Teensy: Current conductance: 0.000000049626518
Teensy: Current conductance: 0.000000046845184
Teensy: Current conductance: 0.000000045032628
Teensy: Current conductance: 0.000000042907558
Teensy: Current conductance: 0.000000040501238
Teensy: Current conductance: 0.000000038501177
Teensy: Current conductance: 0.000000036844877
Teensy: Current conductance: 0.000000035469839
Teensy: Current conductance: 0.000000033688529
Teensy: Current conductance: 0.000000032188485
Teensy: Current conductance: 0.000000030875945
Teensy: Current conductance: 0.000000029532153
Teensy: Current conductance: 0.000000028938384
Teensy: Current conductance: 0.000000028157109
Teensy: Current conductance: 0.000000027438340
Teensy: Current conductance: 0.000000026219553
Teensy: Current conductance: 0.000000026063297
Teensy: Current conductance: 0.000000024938263
Teensy: Current conductance: 0.000000024782008
Teensy: Current conductance: 0.000000023906981
Teensy: Current conductance: 0.000000024219490
Teensy: Current conductance: 0.000000023531969
Teensy: Current conductance: 0.000000023094454
Teensy: Current conductance: 0.000000023438217
Teensy: Current conductance: 0.000000023156957
Teensy: Current conductance: 0.000000022188178
Teensy: Current conductance: 0.000000022469436
Teensy: Current conductance: 0.000000021313152
Teensy: Current conductance: 0.000000021656913
Teensy: Current conductance: 0.000000021719416
Teensy: Current conductance: 0.000000021406906
Teensy: Current conductance: 0.000000021250649
Teensy: Current conductance: 0.000000021594412
""",
"1cccc":"""
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001250038
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001281289
> drain
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001250038
Teensy: Current conductance: 0.000000001218787
Teensy: Current conductance: 0.000000001218787
Teensy: Current conductance: 0.000000001218787
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001187536
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001218787
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001593799
Teensy: Current conductance: 0.000000002031312
Teensy: Current conductance: 0.000000002406324
Teensy: Current conductance: 0.000000003625111
Teensy: Current conductance: 0.000000005093906
Teensy: Current conductance: 0.000000006437697
Teensy: Current conductance: 0.000000007562732
Teensy: Current conductance: 0.000000008719017
Teensy: Current conductance: 0.000000010625325
Teensy: Current conductance: 0.000000012250374
Teensy: Current conductance: 0.000000013250405
Teensy: Current conductance: 0.000000015187965
Teensy: Current conductance: 0.000000017094273
Teensy: Current conductance: 0.000000019000581
Teensy: Current conductance: 0.000000019938110
Teensy: Current conductance: 0.000000022219428
Teensy: Current conductance: 0.000000024000732
Teensy: Current conductance: 0.000000025344525
Teensy: Current conductance: 0.000000028063358
Teensy: Current conductance: 0.000000029625905
Teensy: Current conductance: 0.000000031969726
Teensy: Current conductance: 0.000000034688558
Teensy: Current conductance: 0.000000036251109
Teensy: Current conductance: 0.000000038094914
Teensy: Current conductance: 0.000000040094974
Teensy: Current conductance: 0.000000042688807
Teensy: Current conductance: 0.000000044188848
Teensy: Current conductance: 0.000000046626425
Teensy: Current conductance: 0.000000048751488
Teensy: Current conductance: 0.000000051220315
Teensy: Current conductance: 0.000000053314132
Teensy: Current conductance: 0.000000054720420
Teensy: Current conductance: 0.000000057658010
Teensy: Current conductance: 0.000000059845576
Teensy: Current conductance: 0.000000061595635
Teensy: Current conductance: 0.000000063439444
Teensy: Current conductance: 0.000000065064491
Teensy: Current conductance: 0.000000066533289
Teensy: Current conductance: 0.000000068345834
Teensy: Current conductance: 0.000000069408372
Teensy: Current conductance: 0.000000071658448
Teensy: Current conductance: 0.000000072877228
Teensy: Current conductance: 0.000000074189771
Teensy: Current conductance: 0.000000074846042
Teensy: Current conductance: 0.000000075533556
Teensy: Current conductance: 0.000000074908542
Teensy: Current conductance: 0.000000075814818
Teensy: Current conductance: 0.000000075533556
Teensy: Current conductance: 0.000000075346051
Teensy: Current conductance: 0.000000074939784
Teensy: Current conductance: 0.000000073564749
Teensy: Current conductance: 0.000000073439750
Teensy: Current conductance: 0.000000071970952
Teensy: Current conductance: 0.000000070439661
Teensy: Current conductance: 0.000000069002112
Teensy: Current conductance: 0.000000066439533
Teensy: Current conductance: 0.000000064501968
Teensy: Current conductance: 0.000000062658167
Teensy: Current conductance: 0.000000060064338
Teensy: Current conductance: 0.000000058126776
Teensy: Current conductance: 0.000000054751677
Teensy: Current conductance: 0.000000052845365
Teensy: Current conductance: 0.000000051095313
Teensy: Current conductance: 0.000000047876462
Teensy: Current conductance: 0.000000046188909
Teensy: Current conductance: 0.000000043720085
Teensy: Current conductance: 0.000000042032532
Teensy: Current conductance: 0.000000039594958
Teensy: Current conductance: 0.000000037532395
Teensy: Current conductance: 0.000000036532366
Teensy: Current conductance: 0.000000034032293
Teensy: Current conductance: 0.000000033094761
Teensy: Current conductance: 0.000000032063479
Teensy: Current conductance: 0.000000030875945
Teensy: Current conductance: 0.000000029813410
Teensy: Current conductance: 0.000000028688376
Teensy: Current conductance: 0.000000027657096
Teensy: Current conductance: 0.000000027282084
Teensy: Current conductance: 0.000000026657066
Teensy: Current conductance: 0.000000026313305
Teensy: Current conductance: 0.000000025313275
Teensy: Current conductance: 0.000000025282022
Teensy: Current conductance: 0.000000024875762
Teensy: Current conductance: 0.000000024406996
Teensy: Current conductance: 0.000000023938231
Teensy: Current conductance: 0.000000024031985
Teensy: Current conductance: 0.000000023188209
Teensy: Current conductance: 0.000000022438186
Teensy: Current conductance: 0.000000022656941
Teensy: Current conductance: 0.000000022219428
Teensy: Current conductance: 0.000000022031923
Teensy: Current conductance: 0.000000022094424
Teensy: Current conductance: 0.000000022281931
Teensy: Current conductance: 0.000000021750663
Teensy: Current conductance: 0.000000021563160
"""
,"1ccc":"""
Teensy: Current conductance: 0.000000001250038
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001406293
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001250038
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001218787
Teensy: Current conductance: 0.000000001281289
> drain
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001218787
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001218787
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001250038
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001250038
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001593799
Teensy: Current conductance: 0.000000001843806
Teensy: Current conductance: 0.000000002437574
Teensy: Current conductance: 0.000000003218849
Teensy: Current conductance: 0.000000004625141
Teensy: Current conductance: 0.000000005500168
Teensy: Current conductance: 0.000000006875211
Teensy: Current conductance: 0.000000008500260
Teensy: Current conductance: 0.000000009937804
Teensy: Current conductance: 0.000000011781609
Teensy: Current conductance: 0.000000013125401
Teensy: Current conductance: 0.000000014687949
Teensy: Current conductance: 0.000000016594257
Teensy: Current conductance: 0.000000018406814
Teensy: Current conductance: 0.000000019938110
Teensy: Current conductance: 0.000000022031923
Teensy: Current conductance: 0.000000023750726
Teensy: Current conductance: 0.000000025594533
Teensy: Current conductance: 0.000000027250833
Teensy: Current conductance: 0.000000029375897
Teensy: Current conductance: 0.000000031438461
Teensy: Current conductance: 0.000000033376018
Teensy: Current conductance: 0.000000035469839
Teensy: Current conductance: 0.000000037407389
Teensy: Current conductance: 0.000000039469953
Teensy: Current conductance: 0.000000041876280
Teensy: Current conductance: 0.000000044063846
Teensy: Current conductance: 0.000000045782649
Teensy: Current conductance: 0.000000048220226
Teensy: Current conductance: 0.000000050376542
Teensy: Current conductance: 0.000000052657857
Teensy: Current conductance: 0.000000054720420
Teensy: Current conductance: 0.000000056845490
Teensy: Current conductance: 0.000000058626789
Teensy: Current conductance: 0.000000060314342
Teensy: Current conductance: 0.000000062470662
Teensy: Current conductance: 0.000000064314463
Teensy: Current conductance: 0.000000066158272
Teensy: Current conductance: 0.000000068002080
Teensy: Current conductance: 0.000000068783358
Teensy: Current conductance: 0.000000071439686
Teensy: Current conductance: 0.000000072595967
Teensy: Current conductance: 0.000000073564749
Teensy: Current conductance: 0.000000074596031
Teensy: Current conductance: 0.000000075439800
Teensy: Current conductance: 0.000000076189828
Teensy: Current conductance: 0.000000076096079
Teensy: Current conductance: 0.000000076377333
Teensy: Current conductance: 0.000000076096079
Teensy: Current conductance: 0.000000075939816
Teensy: Current conductance: 0.000000075439800
Teensy: Current conductance: 0.000000074908542
Teensy: Current conductance: 0.000000074127271
Teensy: Current conductance: 0.000000072220956
Teensy: Current conductance: 0.000000070845914
Teensy: Current conductance: 0.000000069033362
Teensy: Current conductance: 0.000000067720812
Teensy: Current conductance: 0.000000065783254
Teensy: Current conductance: 0.000000063501936
Teensy: Current conductance: 0.000000060783108
Teensy: Current conductance: 0.000000059001803
Teensy: Current conductance: 0.000000056064209
Teensy: Current conductance: 0.000000053907897
Teensy: Current conductance: 0.000000051189065
Teensy: Current conductance: 0.000000049189005
Teensy: Current conductance: 0.000000047251444
Teensy: Current conductance: 0.000000044438856
Teensy: Current conductance: 0.000000042470049
Teensy: Current conductance: 0.000000039938723
Teensy: Current conductance: 0.000000038501177
Teensy: Current conductance: 0.000000036813628
Teensy: Current conductance: 0.000000035126074
Teensy: Current conductance: 0.000000033876038
Teensy: Current conductance: 0.000000032969758
Teensy: Current conductance: 0.000000031844724
Teensy: Current conductance: 0.000000030625937
Teensy: Current conductance: 0.000000029813410
Teensy: Current conductance: 0.000000028750877
Teensy: Current conductance: 0.000000028532121
Teensy: Current conductance: 0.000000027469591
Teensy: Current conductance: 0.000000027344587
Teensy: Current conductance: 0.000000026688316
Teensy: Current conductance: 0.000000026000794
Teensy: Current conductance: 0.000000025782038
Teensy: Current conductance: 0.000000025063267
Teensy: Current conductance: 0.000000024719505
Teensy: Current conductance: 0.000000024438247
Teensy: Current conductance: 0.000000024313243
Teensy: Current conductance: 0.000000024281992
Teensy: Current conductance: 0.000000023844478
Teensy: Current conductance: 0.000000023281961
Teensy: Current conductance: 0.000000023781977
Teensy: Current conductance: 0.000000023438217
Teensy: Current conductance: 0.000000023063205
Teensy: Current conductance: 0.000000023000704
Teensy: Current conductance: 0.000000023188209
"""
,"1cc":"""
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001218787
> drain
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001250038
Teensy: Current conductance: 0.000000001250038
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001250038
Teensy: Current conductance: 0.000000001250038
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001218787
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001218787
Teensy: Current conductance: 0.000000001250038
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001218787
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001500046
Teensy: Current conductance: 0.000000001687552
Teensy: Current conductance: 0.000000002250069
Teensy: Current conductance: 0.000000002906339
Teensy: Current conductance: 0.000000003625111
Teensy: Current conductance: 0.000000005031404
Teensy: Current conductance: 0.000000006593952
Teensy: Current conductance: 0.000000008219001
Teensy: Current conductance: 0.000000009125279
Teensy: Current conductance: 0.000000011000336
Teensy: Current conductance: 0.000000013031649
Teensy: Current conductance: 0.000000014219184
Teensy: Current conductance: 0.000000015687979
Teensy: Current conductance: 0.000000017375532
Teensy: Current conductance: 0.000000018656820
Teensy: Current conductance: 0.000000020813136
Teensy: Current conductance: 0.000000022781945
Teensy: Current conductance: 0.000000024532000
Teensy: Current conductance: 0.000000026594563
Teensy: Current conductance: 0.000000028500871
Teensy: Current conductance: 0.000000029844664
Teensy: Current conductance: 0.000000032500992
Teensy: Current conductance: 0.000000034751064
Teensy: Current conductance: 0.000000036126103
Teensy: Current conductance: 0.000000038094914
Teensy: Current conductance: 0.000000040438735
Teensy: Current conductance: 0.000000042720057
Teensy: Current conductance: 0.000000044845120
Teensy: Current conductance: 0.000000046345168
Teensy: Current conductance: 0.000000049095252
Teensy: Current conductance: 0.000000051314068
Teensy: Current conductance: 0.000000053532887
Teensy: Current conductance: 0.000000056126716
Teensy: Current conductance: 0.000000057814269
Teensy: Current conductance: 0.000000059439316
Teensy: Current conductance: 0.000000061220625
Teensy: Current conductance: 0.000000063470694
Teensy: Current conductance: 0.000000065533250
Teensy: Current conductance: 0.000000067408308
Teensy: Current conductance: 0.000000068533346
Teensy: Current conductance: 0.000000070064644
Teensy: Current conductance: 0.000000072064701
Teensy: Current conductance: 0.000000072814728
Teensy: Current conductance: 0.000000074502275
Teensy: Current conductance: 0.000000075721061
Teensy: Current conductance: 0.000000076158578
Teensy: Current conductance: 0.000000076877349
Teensy: Current conductance: 0.000000076783600
Teensy: Current conductance: 0.000000077408622
Teensy: Current conductance: 0.000000077314866
Teensy: Current conductance: 0.000000077158610
Teensy: Current conductance: 0.000000076439832
Teensy: Current conductance: 0.000000075814818
Teensy: Current conductance: 0.000000074939784
Teensy: Current conductance: 0.000000073877260
Teensy: Current conductance: 0.000000072189714
Teensy: Current conductance: 0.000000070845914
Teensy: Current conductance: 0.000000069252117
Teensy: Current conductance: 0.000000067127047
Teensy: Current conductance: 0.000000064876986
Teensy: Current conductance: 0.000000062564411
Teensy: Current conductance: 0.000000060501854
Teensy: Current conductance: 0.000000058283032
Teensy: Current conductance: 0.000000055626703
Teensy: Current conductance: 0.000000053314132
Teensy: Current conductance: 0.000000050470291
Teensy: Current conductance: 0.000000048001464
Teensy: Current conductance: 0.000000045876401
Teensy: Current conductance: 0.000000044095096
Teensy: Current conductance: 0.000000042438799
Teensy: Current conductance: 0.000000040282480
Teensy: Current conductance: 0.000000038344922
Teensy: Current conductance: 0.000000037094885
Teensy: Current conductance: 0.000000035501085
Teensy: Current conductance: 0.000000034438550
Teensy: Current conductance: 0.000000032907259
Teensy: Current conductance: 0.000000031657216
Teensy: Current conductance: 0.000000030625937
Teensy: Current conductance: 0.000000030063422
Teensy: Current conductance: 0.000000029563402
Teensy: Current conductance: 0.000000028563372
Teensy: Current conductance: 0.000000028094608
Teensy: Current conductance: 0.000000027719597
Teensy: Current conductance: 0.000000026844571
Teensy: Current conductance: 0.000000026657066
Teensy: Current conductance: 0.000000026157050
Teensy: Current conductance: 0.000000025594533
Teensy: Current conductance: 0.000000025532030
Teensy: Current conductance: 0.000000024844509
Teensy: Current conductance: 0.000000024782008
Teensy: Current conductance: 0.000000024750758
Teensy: Current conductance: 0.000000024375744
Teensy: Current conductance: 0.000000024688253
Teensy: Current conductance: 0.000000024438247
Teensy: Current conductance: 0.000000024344494
Teensy: Current conductance: 0.000000024031985
Teensy: Current conductance: 0.000000023781977
""",
"11":"""
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001406293
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001406293
Teensy: Current conductance: 0.000000001343791
> drain
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001406293
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001406293
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001406293
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001406293
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001406293
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001406293
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001437544
Teensy: Current conductance: 0.000000001406293
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001406293
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001406293
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001406293
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001406293
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001406293
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001406293
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001406293
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001406293
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001406293
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001406293
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001687552
Teensy: Current conductance: 0.000000002281320
Teensy: Current conductance: 0.000000003281350
Teensy: Current conductance: 0.000000004562640
Teensy: Current conductance: 0.000000006125187
Teensy: Current conductance: 0.000000008062746
Teensy: Current conductance: 0.000000009437788
Teensy: Current conductance: 0.000000010719078
Teensy: Current conductance: 0.000000012125370
Teensy: Current conductance: 0.000000013687919
Teensy: Current conductance: 0.000000014906705
Teensy: Current conductance: 0.000000016438001
Teensy: Current conductance: 0.000000017875546
Teensy: Current conductance: 0.000000019250589
Teensy: Current conductance: 0.000000020156866
Teensy: Current conductance: 0.000000021438156
Teensy: Current conductance: 0.000000021656913
Teensy: Current conductance: 0.000000022844446
Teensy: Current conductance: 0.000000022750696
Teensy: Current conductance: 0.000000023094454
Teensy: Current conductance: 0.000000023125706
Teensy: Current conductance: 0.000000023031953
Teensy: Current conductance: 0.000000022063173
Teensy: Current conductance: 0.000000021500657
Teensy: Current conductance: 0.000000020219368
Teensy: Current conductance: 0.000000018594319
Teensy: Current conductance: 0.000000017250528
Teensy: Current conductance: 0.000000015344220
Teensy: Current conductance: 0.000000012750390
Teensy: Current conductance: 0.000000011156591
Teensy: Current conductance: 0.000000009094028
Teensy: Current conductance: 0.000000006437697
Teensy: Current conductance: 0.000000004187628
Teensy: Current conductance: 0.000000002687582
Teensy: Current conductance: 0.000000001656301
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001406293
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001406293
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001312540
""",
"12":"""
Teensy: Current conductance: 0.000000001406293
Teensy: Current conductance: 0.000000001437544
Teensy: Current conductance: 0.000000001437544
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001406293
> drain
Teensy: Current conductance: 0.000000001406293
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001437544
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001437544
Teensy: Current conductance: 0.000000001406293
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001406293
Teensy: Current conductance: 0.000000001406293
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001406293
Teensy: Current conductance: 0.000000001406293
Teensy: Current conductance: 0.000000001406293
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001437544
Teensy: Current conductance: 0.000000001406293
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001406293
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001406293
Teensy: Current conductance: 0.000000001406293
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001406293
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001406293
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001406293
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001281289
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001406293
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001437544
Teensy: Current conductance: 0.000000001531297
Teensy: Current conductance: 0.000000002218818
Teensy: Current conductance: 0.000000002687582
Teensy: Current conductance: 0.000000003812617
Teensy: Current conductance: 0.000000005093906
Teensy: Current conductance: 0.000000006781457
Teensy: Current conductance: 0.000000008406507
Teensy: Current conductance: 0.000000009656545
Teensy: Current conductance: 0.000000010719078
Teensy: Current conductance: 0.000000012719139
Teensy: Current conductance: 0.000000013719170
Teensy: Current conductance: 0.000000014469192
Teensy: Current conductance: 0.000000016156743
Teensy: Current conductance: 0.000000017313029
Teensy: Current conductance: 0.000000018219307
Teensy: Current conductance: 0.000000019406844
Teensy: Current conductance: 0.000000019938110
Teensy: Current conductance: 0.000000021219400
Teensy: Current conductance: 0.000000021219400
Teensy: Current conductance: 0.000000021656913
Teensy: Current conductance: 0.000000021406906
Teensy: Current conductance: 0.000000021500657
Teensy: Current conductance: 0.000000021125647
Teensy: Current conductance: 0.000000020250619
Teensy: Current conductance: 0.000000019313090
Teensy: Current conductance: 0.000000018344311
Teensy: Current conductance: 0.000000016906766
Teensy: Current conductance: 0.000000015031711
Teensy: Current conductance: 0.000000013031649
Teensy: Current conductance: 0.000000011406598
Teensy: Current conductance: 0.000000009562792
Teensy: Current conductance: 0.000000007312723
Teensy: Current conductance: 0.000000005218910
Teensy: Current conductance: 0.000000003375103
Teensy: Current conductance: 0.000000002312571
Teensy: Current conductance: 0.000000001593799
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001437544
Teensy: Current conductance: 0.000000001406293
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001406293
Teensy: Current conductance: 0.000000001406293
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001312540
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001406293
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001375042
Teensy: Current conductance: 0.000000001343791
Teensy: Current conductance: 0.000000001406293
Teensy: Current conductance: 0.000000001343791
""",
"nw":"""
Current conductance: 0.000000006119978
Current conductance: 0.000000006328318
Current conductance: 0.000000006927294
Current conductance: 0.000000006953337
Current conductance: 0.000000007448144
Current conductance: 0.000000007786696
Current conductance: 0.000000008229418
Current conductance: 0.000000008281503
Current conductance: 0.000000008515885
Current conductance: 0.000000008932564
Current conductance: 0.000000008880479
Current conductance: 0.000000009219032
Current conductance: 0.000000009453413
Current conductance: 0.000000009713839
Current conductance: 0.000000009896135
Current conductance: 0.000000010000305
Current conductance: 0.000000010312815
Current conductance: 0.000000010547198
Current conductance: 0.000000010755537
Current conductance: 0.000000011042004
Current conductance: 0.000000011224301
Current conductance: 0.000000011484726
Current conductance: 0.000000011536811
Current conductance: 0.000000011875363
Current conductance: 0.000000012031617
Current conductance: 0.000000012448296
Current conductance: 0.000000012552467
Current conductance: 0.000000012734763
Current conductance: 0.000000013073316
Current conductance: 0.000000013151443
Current conductance: 0.000000013489994
Current conductance: 0.000000013698334
Current conductance: 0.000000013724377
Current conductance: 0.000000014141057
Current conductance: 0.000000014479610
Current conductance: 0.000000014870245
Current conductance: 0.000000015026499
Current conductance: 0.000000015156713
Current conductance: 0.000000015521307
Current conductance: 0.000000015755690
Current conductance: 0.000000016042156
Current conductance: 0.000000016198412
Current conductance: 0.000000016745302
Current conductance: 0.000000016901557
Current conductance: 0.000000017109896
Current conductance: 0.000000017370324
Current conductance: 0.000000017604705
Current conductance: 0.000000017813043
Current conductance: 0.000000018099511
Current conductance: 0.000000018438064
Current conductance: 0.000000018620360
Current conductance: 0.000000019141208
Current conductance: 0.000000019453719
Current conductance: 0.000000019636015
Current conductance: 0.000000019948525
Current conductance: 0.000000020261036
Current conductance: 0.000000020391248
Current conductance: 0.000000021042309
Current conductance: 0.000000021094396
Current conductance: 0.000000021485031
Current conductance: 0.000000021667327
Current conductance: 0.000000022188177
Current conductance: 0.000000022422560
Current conductance: 0.000000022865281
Current conductance: 0.000000023021537
Current conductance: 0.000000023464256
Current conductance: 0.000000023802810
Current conductance: 0.000000024401787
Current conductance: 0.000000024636169
Current conductance: 0.000000025078890
Current conductance: 0.000000025391399
Current conductance: 0.000000025964333
Current conductance: 0.000000026433101
Current conductance: 0.000000026719565
Current conductance: 0.000000027266458
Current conductance: 0.000000027761265
Current conductance: 0.000000028177942
Current conductance: 0.000000028672751
Current conductance: 0.000000029167557
Current conductance: 0.000000029688408
Current conductance: 0.000000030183212
Current conductance: 0.000000030782189
Current conductance: 0.000000031407211
Current conductance: 0.000000032162440
Current conductance: 0.000000032761417
Current conductance: 0.000000033256224
Current conductance: 0.000000034063540
Current conductance: 0.000000034714599
Current conductance: 0.000000035365662
"""


    # Add more cells like this:
    # "R7 C3": """
    # Current resistance: 9000000.00
    # Current resistance: 8500000.00
    # Current resistance: 8100000.00
    # """,
}


def parse_conductance_block(text):
    conductances_uS = []

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        m = re.search(r"Current resistance:\s*([-+]?\d*\.?\d+)", line)
        if m:
            resistance = float(m.group(1))
            if resistance > 0:
                conductances_uS.append(1e6 / resistance)
            else:
                conductances_uS.append(float("nan"))
            continue

        m = re.search(r"Current conductance:\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)", line)
        if m:
            conductance_siemens = float(m.group(1))
            conductances_uS.append(conductance_siemens * 1e6)
            continue

        m = re.fullmatch(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", line)
        if m:
            resistance = float(line)
            if resistance > 0:
                conductances_uS.append(1e6 / resistance)
            else:
                conductances_uS.append(float("nan"))

    return conductances_uS


plt.figure(figsize=(10, 6))

for label, text in runs.items():
    conductances_uS = parse_conductance_block(text)

    x = range(len(conductances_uS))
    plt.plot(
        x,
        conductances_uS,
        marker="o",
        linewidth=2,
        markersize=4,
        label=label,
    )

plt.xlabel("Read / pulse index")
plt.ylabel("Conductance (uS)")
plt.title("ISPP conductance evolution")
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.show()
