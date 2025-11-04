### models/cpu_cbow_accuracy/model-best

```
ℹ Using CPU
ℹ To switch to GPU 0, use the option: --gpu-id 0

================================== Results ==================================

TOK                 100.00
TEXTCAT (macro F)   77.53 
SPEED               639   


=========================== Textcat F (per label) ===========================

                                  P       R       F
Epistolary Exchange           81.82   65.45   72.73
Objective Statement           70.42   86.21   77.52
Recording of Information      92.31   92.31   92.31
Transmission of Information   69.44   65.79   67.57


======================== Textcat ROC AUC (per label) ========================

                              ROC AUC
Epistolary Exchange              0.86
Objective Statement              0.88
Recording of Information         0.99
Transmission of Information      0.80

```

### models/cpu_cbow_efficiency_2/model-best

```
ℹ Using CPU
ℹ To switch to GPU 0, use the option: --gpu-id 0

================================== Results ==================================

TOK                 100.00
TEXTCAT (macro F)   83.35 
SPEED               105777


=========================== Textcat F (per label) ===========================

                                   P       R       F
Epistolary Exchange            95.12   70.91   81.25
Objective Statement            75.76   86.21   80.65
Recording of Information      100.00   88.46   93.88
Transmission of Information    70.21   86.84   77.65


======================== Textcat ROC AUC (per label) ========================

                              ROC AUC
Epistolary Exchange              0.93
Objective Statement              0.94
Recording of Information         0.99
Transmission of Information      0.95

```

### models/cpu_cbow_efficiency/model-best

```
ℹ Using CPU
ℹ To switch to GPU 0, use the option: --gpu-id 0

================================== Results ==================================

TOK                 100.00
TEXTCAT (macro F)   75.80 
SPEED               107372


=========================== Textcat F (per label) ===========================

                                   P       R       F
Epistolary Exchange            76.79   78.18   77.48
Objective Statement            68.29   96.55   80.00
Recording of Information      100.00   88.46   93.88
Transmission of Information    87.50   36.84   51.85


======================== Textcat ROC AUC (per label) ========================

                              ROC AUC
Epistolary Exchange              0.89
Objective Statement              0.93
Recording of Information         0.96
Transmission of Information      0.90

```

### models/gpu_efficiency/model-best

```
ℹ Using CPU
ℹ To switch to GPU 0, use the option: --gpu-id 0

================================== Results ==================================

TOK                 100.00
TEXTCAT (macro F)   79.29 
SPEED               56    


=========================== Textcat F (per label) ===========================

                                   P       R       F
Epistolary Exchange            84.44   69.09   76.00
Objective Statement            70.27   89.66   78.79
Recording of Information      100.00   88.46   93.88
Transmission of Information    71.43   65.79   68.49


======================== Textcat ROC AUC (per label) ========================

                              ROC AUC
Epistolary Exchange              0.88
Objective Statement              0.92
Recording of Information         0.95
Transmission of Information      0.74

```

### models/gpu_parametricattn/model-best

```
ℹ Using CPU
ℹ To switch to GPU 0, use the option: --gpu-id 0

================================== Results ==================================

TOK                 100.00
TEXTCAT (macro F)   77.54 
SPEED               53    


=========================== Textcat F (per label) ===========================

                                   P       R       F
Epistolary Exchange            73.33   80.00   76.52
Objective Statement            72.22   89.66   80.00
Recording of Information      100.00   92.31   96.00
Transmission of Information    80.95   44.74   57.63


======================== Textcat ROC AUC (per label) ========================

                              ROC AUC
Epistolary Exchange              0.88
Objective Statement              0.89
Recording of Information         0.99
Transmission of Information      0.82

```

### models/cpu_cbow_accuracy_concat/model-best

```
ℹ Using CPU
ℹ To switch to GPU 0, use the option: --gpu-id 0

================================== Results ==================================

TOK                 100.00
TEXTCAT (macro F)   96.33 
SPEED               1529  


=========================== Textcat F (per label) ===========================

                                   P        R       F
Epistolary Exchange            94.92    94.92   94.92
Objective Statement            97.67    93.33   95.45
Recording of Information      100.00    96.15   98.04
Transmission of Information    94.00   100.00   96.91


======================== Textcat ROC AUC (per label) ========================

                              ROC AUC
Epistolary Exchange              0.99
Objective Statement              1.00
Recording of Information         1.00
Transmission of Information      1.00

```

### models/cpu_cbow_efficiency_concat/model-best

```
ℹ Using CPU
ℹ To switch to GPU 0, use the option: --gpu-id 0

================================== Results ==================================

TOK                 100.00
TEXTCAT (macro F)   95.74 
SPEED               317849


=========================== Textcat F (per label) ===========================

                                   P       R       F
Epistolary Exchange            95.00   96.61   95.80
Objective Statement            93.62   97.78   95.65
Recording of Information      100.00   96.15   98.04
Transmission of Information    95.56   91.49   93.48


======================== Textcat ROC AUC (per label) ========================

                              ROC AUC
Epistolary Exchange              1.00
Objective Statement              1.00
Recording of Information         1.00
Transmission of Information      1.00

```

### models/cpu_parametricattn_concat/model-best

```
ℹ Using CPU
ℹ To switch to GPU 0, use the option: --gpu-id 0

================================== Results ==================================

TOK                 100.00
TEXTCAT (macro F)   97.31 
SPEED               1558  


=========================== Textcat F (per label) ===========================

                                   P        R       F
Epistolary Exchange            95.08    98.31   96.67
Objective Statement            97.83   100.00   98.90
Recording of Information      100.00    96.15   98.04
Transmission of Information    97.78    93.62   95.65


======================== Textcat ROC AUC (per label) ========================

                              ROC AUC
Epistolary Exchange              1.00
Objective Statement              1.00
Recording of Information         1.00
Transmission of Information      1.00

```

### models/cpu_parametricattn__nostatic_concat/model-best

```
ℹ Using CPU
ℹ To switch to GPU 0, use the option: --gpu-id 0

================================== Results ==================================

TOK                 100.00
TEXTCAT (macro F)   99.02 
SPEED               1577  


=========================== Textcat F (per label) ===========================

                                   P        R        F
Epistolary Exchange            98.31    98.31    98.31
Objective Statement            97.78    97.78    97.78
Recording of Information      100.00   100.00   100.00
Transmission of Information   100.00   100.00   100.00


======================== Textcat ROC AUC (per label) ========================

                              ROC AUC
Epistolary Exchange              1.00
Objective Statement              1.00
Recording of Information         1.00
Transmission of Information      1.00

```

### models/gpu_accuracy_concat/model-best

```
ℹ Using CPU
ℹ To switch to GPU 0, use the option: --gpu-id 0

================================== Results ==================================

TOK                 100.00
TEXTCAT (macro F)   99.52 
SPEED               35    


=========================== Textcat F (per label) ===========================

                                   P        R        F
Epistolary Exchange            98.33   100.00    99.16
Objective Statement           100.00   100.00   100.00
Recording of Information      100.00   100.00   100.00
Transmission of Information   100.00    97.87    98.92


======================== Textcat ROC AUC (per label) ========================

                              ROC AUC
Epistolary Exchange              1.00
Objective Statement              1.00
Recording of Information         1.00
Transmission of Information      1.00

```

### models/gpu_efficiency_concat/model-best

```
ℹ Using CPU
ℹ To switch to GPU 0, use the option: --gpu-id 0

================================== Results ==================================

TOK                 100.00
TEXTCAT (macro F)   99.51 
SPEED               45    


=========================== Textcat F (per label) ===========================

                                   P        R        F
Epistolary Exchange           100.00    98.31    99.15
Objective Statement            97.83   100.00    98.90
Recording of Information      100.00   100.00   100.00
Transmission of Information   100.00   100.00   100.00


======================== Textcat ROC AUC (per label) ========================

                              ROC AUC
Epistolary Exchange              1.00
Objective Statement              1.00
Recording of Information         1.00
Transmission of Information      1.00

```

### models/gpu_parametricattn_concat/model-best

```
ℹ Using CPU
ℹ To switch to GPU 0, use the option: --gpu-id 0

================================== Results ==================================

TOK                 100.00
TEXTCAT (macro F)   98.44 
SPEED               45    


=========================== Textcat F (per label) ===========================

                                   P        R        F
Epistolary Exchange           100.00    98.31    99.15
Objective Statement            93.75   100.00    96.77
Recording of Information      100.00   100.00   100.00
Transmission of Information   100.00    95.74    97.83


======================== Textcat ROC AUC (per label) ========================

                              ROC AUC
Epistolary Exchange              0.99
Objective Statement              1.00
Recording of Information         1.00
Transmission of Information      1.00

```

### models/gpu_parametricattn_concat_top3/model-best

```
ℹ Using CPU
ℹ To switch to GPU 0, use the option: --gpu-id 0

================================== Results ==================================

TOK                 100.00
TEXTCAT (macro F)   84.56 
SPEED               60    


=========================== Textcat F (per label) ===========================

                                  P       R       F
Epistolary Exchange           87.27   80.00   83.48
Objective Statement           80.00   78.05   79.01
Recording of Information      90.62   90.62   90.62
Transmission of Information   80.00   90.91   85.11


======================== Textcat ROC AUC (per label) ========================

                              ROC AUC
Epistolary Exchange              0.91
Objective Statement              0.92
Recording of Information         0.94
Transmission of Information      0.92

```

