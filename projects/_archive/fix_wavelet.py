import re
with open('bench.py','r') as f:
    text=f.read()
# replace first occurrence in main_fev
text = text.replace('''        "subband_d1": (fit_subbands, lambda m,h: pred_subband(m,h,"d1")),
        "wavelet_pooled": (fit_pooled, pred_pooled),
    }
    task_results=[]''', '''        "subband_d1": (fit_subbands, lambda m,h: pred_subband(m,h,"d1")),
    }
    if _HAS_ELM:
        fits["wavelet_pooled"] = (fit_pooled, pred_pooled)
    task_results=[]''', 1)
# replace second occurrence in main
text = text.replace('''        "subband_d1": (fit_subbands, lambda m, h: pred_subband(m, h, "d1")),
        "wavelet_pooled": (fit_pooled, pred_pooled),
    }
    if _HAS_BIGDICT:''', '''        "subband_d1": (fit_subbands, lambda m, h: pred_subband(m, h, "d1")),
    }
    if _HAS_ELM:
        fits["wavelet_pooled"] = (fit_pooled, pred_pooled)
    if _HAS_BIGDICT:''', 1)
with open('bench.py','w') as f:
    f.write(text)
print('done')
